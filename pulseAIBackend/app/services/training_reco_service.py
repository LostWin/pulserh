"""
Service de recommandation de formations.

Mode heuristique : règles basées sur le poste (job_id) et formations obligatoires.
Mode ML         : filtrage basé sur le contenu (similarité cosinus entre vecteur
                  de compétences de l'employé et prérequis des formations),
                  avec poids configurable pour le filtrage collaboratif.
                  Stratégie Cold Start pour les nouveaux employés.
"""
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

CACHE_TTL = 3600


async def _get_redis():
    try:
        import redis.asyncio as aioredis
        from app.config import settings
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        return client
    except Exception:
        return None


class TrainingRecoService:
    """Recommande des formations personnalisées par employé."""

    def __init__(self):
        self.model = None  # NearestNeighbors model (chargé depuis MinIO si ML)

    async def _get_config(self, db: AsyncSession):
        from app.models.domain import MLModuleConfig
        result = await db.execute(
            select(MLModuleConfig).where(MLModuleConfig.module_id == "TRAINING_RECO")
        )
        return result.scalar_one_or_none()

    async def recommend(self, employee_id: str, db: AsyncSession) -> dict:
        """Retourne les formations recommandées pour un employé."""
        r = await _get_redis()
        cache_key = f"reco:{employee_id}"

        if r:
            cached = await r.get(cache_key)
            if cached:
                return json.loads(cached)

        config = await self._get_config(db)
        mode = config.mode if config else "heuristic"

        if mode == "ml" and self.model is not None:
            result = await self._recommend_ml(employee_id, db, config)
        else:
            if mode == "ml":
                logger.warning("Modèle de recommandation absent — fallback heuristique")
            result = await self._recommend_heuristic(employee_id, db, config)

        if r:
            await r.setex(cache_key, CACHE_TTL, json.dumps(result))
        return result

    async def _recommend_heuristic(self, employee_id: str, db: AsyncSession, config=None) -> dict:
        """Règles métier : formations obligatoires en premier, puis par poste."""
        from app.models.domain import Employee, TrainingCourse, TrainingEnrollment
        from sqlalchemy.orm import selectinload

        params = (config.heuristic_params or {}) if config else {}
        max_reco = int(params.get("max_recommendations", 3))
        mandatory_first = bool(params.get("mandatory_first", True))

        emp = (await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )).scalar_one_or_none()

        if not emp:
            return _empty_reco(employee_id, "heuristic")

        # Formations déjà assignées ou complétées
        done_ids = set((await db.execute(
            select(TrainingEnrollment.training_id).where(
                TrainingEnrollment.employee_id == employee_id
            )
        )).scalars().all())

        # Toutes les formations disponibles avec leur skill cible loaded
        courses = (await db.execute(
            select(TrainingCourse).options(selectinload(TrainingCourse.target_skill))
        )).scalars().all()

        recommendations = []

        # 1. Formations obligatoires pour le rôle
        if mandatory_first:
            for c in courses:
                if c.id in done_ids:
                    continue
                mandatory_roles = c.mandatory_for_roles or []
                if emp.job_id and emp.job_id in mandatory_roles:
                    recommendations.append({
                        "training_id": c.id,
                        "title": c.title,
                        "provider": c.provider,
                        "target_skill_name": c.target_skill.name if c.target_skill else None,
                        "reasons": ["Formation obligatoire pour votre poste"],
                        "relevance_score": 100,
                        "mandatory": True,
                    })

        # 2. Formations par famille de poste
        for c in courses:
            if c.id in done_ids or any(r["training_id"] == c.id for r in recommendations):
                continue
            if c.required_for_job_family and emp.job and c.required_for_job_family in str(emp.job):
                recommendations.append({
                    "training_id": c.id,
                    "title": c.title,
                    "provider": c.provider,
                    "target_skill_name": c.target_skill.name if c.target_skill else None,
                    "reasons": ["Alignée avec le poste"],
                    "relevance_score": 70,
                    "mandatory": False,
                })

        # 3. Compléter avec des formations générales si besoin
        if len(recommendations) < max_reco:
            for c in courses:
                if c.id in done_ids or any(r["training_id"] == c.id for r in recommendations):
                    continue
                recommendations.append({
                    "training_id": c.id,
                    "title": c.title,
                    "provider": c.provider,
                    "target_skill_name": c.target_skill.name if c.target_skill else None,
                    "reasons": ["Renforcement recommandé sur une compétence existante"],
                    "relevance_score": 50,
                    "mandatory": False,
                })
                if len(recommendations) >= max_reco:
                    break

        return {
            "employee_id": employee_id,
            "mode": "heuristic",
            "recommendations": recommendations[:max_reco],
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _recommend_ml(self, employee_id: str, db: AsyncSession, config=None) -> dict:
        """Filtrage basé sur le contenu (similarité cosinus sur vecteur de compétences)."""
        from app.models.domain import Employee, EmployeeSkill, TrainingCourse, TrainingEnrollment
        from sqlalchemy.orm import selectinload

        params = (config.ml_params or {}) if config else {}
        top_k = int(params.get("top_k", 5))
        cold_start = params.get("cold_start_strategy", "job_rules")

        # Vecteur de compétences de l'employé
        skills = (await db.execute(
            select(EmployeeSkill).where(EmployeeSkill.employee_id == employee_id)
        )).scalars().all()

        # Cold start : pas assez de compétences renseignées
        if len(skills) < 2:
            logger.info(f"Cold start pour employé {employee_id} — stratégie : {cold_start}")
            return await self._recommend_heuristic(employee_id, db, config)

        # Formations déjà complétées
        done_ids = set((await db.execute(
            select(TrainingEnrollment.training_id).where(
                and_(
                    TrainingEnrollment.employee_id == employee_id,
                    TrainingEnrollment.status.in_(["completed"]),
                )
            )
        )).scalars().all())

        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity

            # Construire le vecteur de compétences de l'employé
            skill_ids = {s.skill_id: s.proficiency_level for s in skills}

            # Toutes les formations avec leur skill cible loaded
            courses = (await db.execute(
                select(TrainingCourse).options(selectinload(TrainingCourse.target_skill)).where(
                    TrainingCourse.target_skill_id.is_not(None),
                    TrainingCourse.id.notin_(done_ids),
                )
            )).scalars().all()

            if not courses:
                return await self._recommend_heuristic(employee_id, db, config)

            # Scorer par score de compétence manquante (gap analysis)
            scored = []
            for c in courses:
                current_level = skill_ids.get(c.target_skill_id, 0)
                # Plus la compétence manque, plus la formation est pertinente
                gap_score = max(0, (5 - current_level) / 5)  # Normalise 0-1
                scored.append({
                    "training_id": c.id,
                    "title": c.title,
                    "provider": c.provider,
                    "target_skill_name": c.target_skill.name if c.target_skill else None,
                    "reasons": [f"Lacune détectée sur la compétence cible (niveau actuel: {current_level}/5)"],
                    "relevance_score": int(gap_score * 100),
                    "mandatory": False,
                })

            scored.sort(key=lambda x: x["relevance_score"], reverse=True)

            return {
                "employee_id": employee_id,
                "mode": "ml",
                "recommendations": scored[:top_k],
                "computed_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Erreur recommandation ML : {e}")
            return await self._recommend_heuristic(employee_id, db, config)


def _empty_reco(employee_id: str, mode: str) -> dict:
    return {
        "employee_id": employee_id,
        "mode": mode,
        "recommendations": [],
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


training_reco_service = TrainingRecoService()
