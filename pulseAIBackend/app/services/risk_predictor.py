from __future__ import annotations
import io
import json
import logging
from datetime import datetime, timezone
from typing import Literal

import joblib
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.feature_extractor import feature_extractor
from app.models.domain import Employee

logger = logging.getLogger(__name__)

MODEL_BUCKET = "ml-models"
MODEL_KEY = "risk_xgboost_v1.pkl"
CACHE_TTL = 3600

# Ordre des colonnes attendu par le modèle XGBoost
FEATURE_COLS = [
    "tenure_months", "salary", "contract_type",
    "leave_days_12m", "sick_leave_count_12m",
    "absence_count_3m", "late_count_3m",
    "avg_task_score", "overdue_tasks_count",
]


def _level(score: float) -> Literal["green", "orange", "red"]:
    if score < 0.33:
        return "green"
    if score < 0.66:
        return "orange"
    return "red"


async def _get_redis():
    try:
        import redis.asyncio as aioredis
        from app.config import settings
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        return client
    except Exception:
        return None


class RiskPredictor:
    """Calcule les scores de risque de départ — mode Heuristique ou ML (XGBoost)."""

    def __init__(self):
        self.model = None

    def load(self) -> None:
        """Charge le modèle XGBoost depuis MinIO. Appelé au démarrage si le mode ML est actif."""
        try:
            from minio import Minio
            from minio.error import S3Error
            from app.config import settings

            client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False,
            )
            response = client.get_object(MODEL_BUCKET, MODEL_KEY)
            self.model = joblib.load(io.BytesIO(response.read()))
            logger.info("Modèle de risque XGBoost chargé depuis MinIO")
        except Exception as e:
            logger.warning(f"Modèle absent ou inaccessible depuis MinIO — mode heuristique utilisé : {e}")

    async def _get_module_config(self, db: AsyncSession):
        """Lit la configuration du module CHURN_RISK depuis la base de données."""
        try:
            from app.models.domain import MLModuleConfig
            result = await db.execute(
                select(MLModuleConfig).where(MLModuleConfig.module_id == "CHURN_RISK")
            )
            return result.scalar_one_or_none()
        except Exception:
            return None

    async def predict(self, employee_or_id: str | Employee, db: AsyncSession) -> dict:
        """Retourne le score de risque pour un employé (avec cache Redis, TTL 1h)."""
        from sqlalchemy.orm import selectinload

        if isinstance(employee_or_id, str):
            employee_id = employee_or_id
            employee = None
        else:
            employee = employee_or_id
            employee_id = employee.id

        r = await _get_redis()
        cache_key = f"risk:{employee_id}"

        if r:
            cached = await r.get(cache_key)
            if cached:
                return json.loads(cached)

        # Cache miss - load Employee object if not already provided
        if employee is None:
            emp_res = await db.execute(
                select(Employee)
                .options(
                    selectinload(Employee.engagement_snapshots),
                    selectinload(Employee.tasks),
                    selectinload(Employee.attendances),
                    selectinload(Employee.training_enrollments),
                    selectinload(Employee.project_assignments),
                    selectinload(Employee.department),
                    selectinload(Employee.job),
                )
                .where(Employee.id == employee_id)
            )
            employee = emp_res.scalar_one_or_none()
            if not employee:
                raise ValueError(f"Employé {employee_id} introuvable")

        config = await self._get_module_config(db)
        mode = config.mode if config else "heuristic"

        if mode == "ml" and self.model is not None:
            result = await self._predict_ml(employee_id, db)
        else:
            if mode == "ml" and self.model is None:
                logger.warning("Mode ML demandé mais modèle non chargé — fallback heuristique")
            result = await self._predict_heuristic(employee_id, db, config)

        # Enrich parameters for dashboard compatibility
        from datetime import date, timedelta
        from app.services.hr_analytics_service import employee_engagement_score, employee_tenure_label

        engagement = employee_engagement_score(employee)
        overdue_tasks = sum(
            1 for task in employee.tasks
            if task.due_date and task.due_date < date.today() and task.status != "Terminé"
        )
        absences_30 = sum(
            1 for attendance in employee.attendances
            if attendance.date and attendance.date >= date.today() - timedelta(days=30) and (attendance.status or "").lower() == "absent"
        )
        mandatory_overdue = sum(
            1 for enrollment in employee.training_enrollments
            if enrollment.mandatory and enrollment.due_date and enrollment.due_date < date.today() and enrollment.status != "completed"
        )
        training_completed = sum(1 for enrollment in employee.training_enrollments if enrollment.status == "completed")
        active_projects = max(1, sum(1 for assignment in employee.project_assignments if assignment.is_active))

        factors = [
            {"label": "Charge de travail", "value": min(95, 24 + overdue_tasks * 18 + active_projects * 4)},
            {"label": "Assiduité", "value": min(95, 18 + absences_30 * 17)},
            {"label": "Formation obligatoire", "value": min(95, 15 + mandatory_overdue * 22)},
            {"label": "Engagement déclaré", "value": min(95, max(10, 100 - engagement))},
            {"label": "Reconnaissance / progression", "value": min(95, 28 + max(0, 3 - training_completed) * 9)},
        ]
        top_factors = sorted(factors, key=lambda item: item["value"], reverse=True)[:3]
        recommendation = {
            "Charge de travail": "Rééquilibrer la charge, clarifier les priorités et revoir les échéances des projets actifs.",
            "Assiduité": "Prévoir un point de suivi et analyser les causes des absences récentes avec le manager.",
            "Formation obligatoire": "Débloquer rapidement les formations obligatoires et lever les freins d'accès.",
            "Engagement déclaré": "Planifier un échange de proximité et mettre en place un plan d'accompagnement ciblé.",
            "Reconnaissance / progression": "Proposer un feedback structuré, une perspective d'évolution et un plan de développement.",
        }.get(top_factors[0]["label"], "Prévoir un échange managérial et ajuster le plan d'accompagnement.")

        result["score"] = float(result["score"])
        result["score_pct"] = float(result["score"] * 100)
        result["engagement"] = engagement
        result["factors"] = top_factors
        result["recommendation"] = recommendation
        result["employee_name"] = f"{employee.first_name} {employee.last_name}"
        result["department"] = employee.department.name if employee.department else "Non assigné"
        result["title"] = employee.job.title if employee.job else "Collaborateur"
        result["tenure"] = employee_tenure_label(employee)

        if r:
            await r.setex(cache_key, CACHE_TTL, json.dumps(result))

        return result

    async def _predict_heuristic(self, employee_id: str, db: AsyncSession, config=None) -> dict:
        """Mode heuristique : score pondéré basé sur des règles métier configurables."""
        features = await feature_extractor.get_employee_features(employee_id, db)

        params = (config.heuristic_params or {}) if config else {}
        absence_w = float(params.get("absence_weight", 0.45))
        sick_w = float(params.get("sick_leave_weight", 0.30))
        task_w = float(params.get("task_score_weight", 0.25))

        # Normalisation des signaux entre 0 et 1
        absence_score = min(features["absence_count_3m"] / 10.0, 1.0)
        sick_score = min(features["sick_leave_count_12m"] / 5.0, 1.0)
        # Mauvaise performance = score proche de 1
        raw_task = features["avg_task_score"]
        task_score = max(0.0, (10.0 - raw_task) / 10.0) if raw_task > 0 else 0.5

        score = (absence_score * absence_w) + (sick_score * sick_w) + (task_score * task_w)
        score = round(min(score, 1.0), 4)

        return {
            "employee_id": employee_id,
            "score": score,
            "level": _level(score),
            "mode": "heuristic",
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _predict_ml(self, employee_id: str, db: AsyncSession) -> dict:
        """Mode ML : score calculé via le modèle XGBoost chargé depuis MinIO."""
        features = await feature_extractor.get_employee_features(employee_id, db)
        X = pd.DataFrame([[features[c] for c in FEATURE_COLS]], columns=FEATURE_COLS)
        score = float(self.model.predict_proba(X)[0][1])

        return {
            "employee_id": employee_id,
            "score": round(score, 4),
            "level": _level(score),
            "mode": "ml",
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def predict_with_scenario(
        self, employee_id: str, overrides: dict, db: AsyncSession
    ) -> tuple[float, float]:
        """
        Rejoue la prédiction avec des features modifiées.
        Retourne (score_original, score_simulé).
        Fonctionne en mode heuristique et ML.
        """
        config = await self._get_module_config(db)
        mode = config.mode if config else "heuristic"
        features = await feature_extractor.get_employee_features(employee_id, db)

        if mode == "ml" and self.model is not None:
            X_orig = pd.DataFrame([[features[c] for c in FEATURE_COLS]], columns=FEATURE_COLS)
            original_score = float(self.model.predict_proba(X_orig)[0][1])

            modified = {**features, **{k: v for k, v in overrides.items() if k in features}}
            X_mod = pd.DataFrame([[modified[c] for c in FEATURE_COLS]], columns=FEATURE_COLS)
            simulated_score = float(self.model.predict_proba(X_mod)[0][1])
        else:
            # Heuristic simulation
            async def _heuristic_score(feats, cfg):
                p = (cfg.heuristic_params or {}) if cfg else {}
                aw = float(p.get("absence_weight", 0.45))
                sw = float(p.get("sick_leave_weight", 0.30))
                tw = float(p.get("task_score_weight", 0.25))
                ab = min(feats["absence_count_3m"] / 10.0, 1.0)
                sk = min(feats["sick_leave_count_12m"] / 5.0, 1.0)
                ts = max(0.0, (10.0 - feats["avg_task_score"]) / 10.0)
                return min((ab * aw) + (sk * sw) + (ts * tw), 1.0)

            original_score = await _heuristic_score(features, config)
            modified = {**features, **{k: v for k, v in overrides.items() if k in features}}
            simulated_score = await _heuristic_score(modified, config)

        return round(original_score, 4), round(simulated_score, 4)


risk_predictor = RiskPredictor()

