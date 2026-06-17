"""
Service d'analyse prédictive de l'absentéisme.

Mode heuristique : moyenne glissante configurable sur les N derniers jours.
Mode ML         : modèle Prophet (série temporelle) ou Régression Poisson,
                  agrégé au niveau département (RGPD obligatoire).
"""
import json
import logging
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

CACHE_TTL = 1800  # 30 minutes


async def _get_redis():
    try:
        import redis.asyncio as aioredis
        from app.config import settings
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        return client
    except Exception:
        return None


class AbsenteeismService:
    """Prédit et analyse le risque d'absentéisme, agrégé par département."""

    def __init__(self):
        self.model = None

    async def _get_config(self, db: AsyncSession):
        from app.models.domain import MLModuleConfig
        result = await db.execute(
            select(MLModuleConfig).where(MLModuleConfig.module_id == "ABSENTEEISM")
        )
        return result.scalar_one_or_none()

    async def get_department_forecast(
        self, department_id: str, db: AsyncSession
    ) -> dict:
        """
        Retourne la prévision d'absentéisme pour un département.
        Agrégation obligatoire — jamais de score individuel exposé.
        """
        r = await _get_redis()
        cache_key = f"absenteeism:dept:{department_id}"

        if r:
            cached = await r.get(cache_key)
            if cached:
                return json.loads(cached)

        config = await self._get_config(db)
        mode = config.mode if config else "heuristic"

        if mode == "ml" and self.model is not None:
            result = await self._forecast_ml(department_id, db, config)
        else:
            if mode == "ml":
                logger.warning("Mode ML demandé mais modèle absent — fallback heuristique")
            result = await self._forecast_heuristic(department_id, db, config)

        if r:
            await r.setex(cache_key, CACHE_TTL, json.dumps(result))

        return result

    async def _forecast_heuristic(
        self, department_id: str, db: AsyncSession, config=None
    ) -> dict:
        """Calcule le taux d'absentéisme moyen sur une fenêtre glissante configurable."""
        from app.models.domain import Attendance, Employee

        params = (config.heuristic_params or {}) if config else {}
        window_days = int(params.get("rolling_window_days", 90))
        threshold = int(params.get("threshold_absences", 5))
        alert_threshold = float(config.alert_threshold if config else 0.60)

        since = date.today() - timedelta(days=window_days)

        # Employés du département
        emp_ids = (await db.execute(
            select(Employee.id).where(Employee.department_id == department_id, Employee.status == "actif")
        )).scalars().all()

        if not emp_ids:
            return _empty_forecast(department_id, "heuristic")

        # Compter les absences
        absences = (await db.execute(
            select(func.count()).select_from(Attendance).where(
                and_(
                    Attendance.employee_id.in_(emp_ids),
                    Attendance.date >= since,
                    Attendance.status == "Absent",
                )
            )
        )).scalar() or 0

        total_days_possible = len(emp_ids) * window_days
        absence_rate = absences / total_days_possible if total_days_possible > 0 else 0.0

        at_risk_count = sum(1 for _ in range(len(emp_ids)) if absences / max(len(emp_ids), 1) >= threshold)

        result = {
            "department_id": department_id,
            "mode": "heuristic",
            "window_days": window_days,
            "absence_rate": round(absence_rate, 4),
            "total_absences": absences,
            "employee_count": len(emp_ids),
            "at_risk": absence_rate > alert_threshold,
            "forecast_30d": None,  # Pas de prévision en mode heuristique
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
        return result

    async def _forecast_ml(
        self, department_id: str, db: AsyncSession, config=None
    ) -> dict:
        """Prévision via le modèle chargé (Prophet ou Poisson)."""
        from app.models.domain import Attendance, Employee

        params = (config.ml_params or {}) if config else {}
        horizon = int(params.get("forecast_horizon_days", 30))

        emp_ids = (await db.execute(
            select(Employee.id).where(Employee.department_id == department_id, Employee.status == "actif")
        )).scalars().all()

        if not emp_ids or self.model is None:
            return await self._forecast_heuristic(department_id, db, config)

        # Données historiques pour le modèle
        rows = (await db.execute(
            select(Attendance.date, func.count().label("n_absent"))
            .where(
                and_(
                    Attendance.employee_id.in_(emp_ids),
                    Attendance.status == "Absent",
                )
            )
            .group_by(Attendance.date)
            .order_by(Attendance.date)
        )).all()

        if len(rows) < 30:
            logger.warning(f"Données insuffisantes pour le département {department_id} — fallback heuristique")
            return await self._forecast_heuristic(department_id, db, config)

        try:
            import pandas as pd
            df = pd.DataFrame(rows, columns=["ds", "y"])
            df["ds"] = pd.to_datetime(df["ds"])

            # Prédiction sur l'horizon configuré
            future = self.model.make_future_dataframe(periods=horizon)
            forecast = self.model.predict(future)
            future_rows = forecast[forecast["ds"] > pd.Timestamp.today()].tail(horizon)

            predicted_absences = int(future_rows["yhat"].clip(0).sum())
            total_days_possible = len(emp_ids) * horizon
            predicted_rate = predicted_absences / total_days_possible if total_days_possible > 0 else 0.0

            alert_threshold = float(config.alert_threshold if config else 0.60)

            return {
                "department_id": department_id,
                "mode": "ml",
                "model_type": params.get("model_type", "prophet"),
                "absence_rate": round(float(df["y"].mean() / max(len(emp_ids), 1)), 4),
                "employee_count": len(emp_ids),
                "at_risk": predicted_rate > alert_threshold,
                "forecast_30d": {
                    "predicted_absences": predicted_absences,
                    "predicted_rate": round(predicted_rate, 4),
                },
                "computed_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Erreur prédiction ML absentéisme : {e}")
            return await self._forecast_heuristic(department_id, db, config)

    async def get_all_departments_forecast(self, db: AsyncSession) -> List[dict]:
        """Retourne la prévision pour tous les départements actifs."""
        from app.models.domain import Department
        dept_ids = (await db.execute(select(Department.id))).scalars().all()
        results = []
        for dept_id in dept_ids:
            try:
                results.append(await self.get_department_forecast(dept_id, db))
            except Exception as e:
                logger.error(f"Erreur dept {dept_id}: {e}")
        return results


def _empty_forecast(department_id: str, mode: str) -> dict:
    return {
        "department_id": department_id,
        "mode": mode,
        "absence_rate": 0.0,
        "employee_count": 0,
        "at_risk": False,
        "forecast_30d": None,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


absenteeism_service = AbsenteeismService()
