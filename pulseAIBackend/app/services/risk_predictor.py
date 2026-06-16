import io
import json
import logging
from datetime import datetime, timezone
from typing import Literal

import joblib
import pandas as pd
from minio import Minio
from minio.error import S3Error
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.feature_extractor import feature_extractor

logger = logging.getLogger(__name__)

MODEL_BUCKET = "ml-models"
MODEL_KEY = "risk_xgboost_v1.pkl"
CACHE_TTL = 3600

# Ordre des colonnes attendu par le modèle
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
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        return client
    except Exception:
        return None


class RiskPredictor:
    """Charge le modèle XGBoost depuis MinIO et calcule les scores de risque."""

    def __init__(self):
        self.model = None

    def load(self) -> None:
        """Charge le modèle en mémoire depuis MinIO. Appelé au démarrage de l'application."""
        try:
            client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False,
            )
            response = client.get_object(MODEL_BUCKET, MODEL_KEY)
            self.model = joblib.load(io.BytesIO(response.read()))
            logger.info("Modèle de risque chargé depuis MinIO")
        except S3Error:
            logger.warning("Modèle absent de MinIO — lancer la tâche d'entraînement d'abord")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle : {e}")

    async def predict(self, employee_id: str, db: AsyncSession) -> dict:
        """Retourne le score de risque pour un employé (avec cache Redis, TTL 1h)."""
        r = await _get_redis()
        cache_key = f"risk:{employee_id}"

        if r:
            cached = await r.get(cache_key)
            if cached:
                return json.loads(cached)

        if self.model is None:
            raise RuntimeError("Modèle non disponible — lancer la tâche d'entraînement d'abord")

        features = await feature_extractor.get_employee_features(employee_id, db)
        X = pd.DataFrame([[features[c] for c in FEATURE_COLS]], columns=FEATURE_COLS)
        score = float(self.model.predict_proba(X)[0][1])

        result = {
            "employee_id": employee_id,
            "score": round(score, 4),
            "level": _level(score),
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

        if r:
            await r.setex(cache_key, CACHE_TTL, json.dumps(result))

        return result

    async def predict_with_scenario(
        self, employee_id: str, overrides: dict, db: AsyncSession
    ) -> tuple[float, float]:
        """
        Rejoue la prédiction avec des features modifiées.
        Retourne (score_original, score_simulé).
        """
        if self.model is None:
            raise RuntimeError("Modèle non disponible — lancer la tâche d'entraînement d'abord")

        features = await feature_extractor.get_employee_features(employee_id, db)

        X_orig = pd.DataFrame([[features[c] for c in FEATURE_COLS]], columns=FEATURE_COLS)
        original_score = float(self.model.predict_proba(X_orig)[0][1])

        modified = {**features, **{k: v for k, v in overrides.items() if k in features}}
        X_mod = pd.DataFrame([[modified[c] for c in FEATURE_COLS]], columns=FEATURE_COLS)
        simulated_score = float(self.model.predict_proba(X_mod)[0][1])

        return round(original_score, 4), round(simulated_score, 4)


risk_predictor = RiskPredictor()
