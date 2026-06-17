"""
Tâche d'entraînement du modèle de détection d'anomalies IA (Isolation Forest).

Collecte les features comportementales des événements d'observabilité IA
des 30 derniers jours, entraîne un modèle Isolation Forest sur les patterns normaux,
et le sauvegarde dans MinIO.
"""
import asyncio
import io
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

MODEL_BUCKET = "ml-models"
MODEL_KEY = "anomaly_isof_v1.pkl"
MIN_SAMPLES = 50


async def _load_behavior_data():
    """Charge les features comportementales des 30 derniers jours."""
    from app.database import AsyncSessionLocal
    from app.models.domain import AIObservabilityEvent
    from sqlalchemy import select, and_, func

    since = datetime.now(timezone.utc) - timedelta(days=30)

    async with AsyncSessionLocal() as db:
        # Agrégation par utilisateur par heure
        rows = (await db.execute(
            select(
                AIObservabilityEvent.user_id,
                func.sum(AIObservabilityEvent.tokens_used).label("total_tokens"),
                func.count().label("request_count"),
                func.avg(AIObservabilityEvent.duration_ms).label("avg_duration_ms"),
                func.sum(
                    (AIObservabilityEvent.status == "error").cast("int")
                ).label("error_count"),
            )
            .where(AIObservabilityEvent.created_at >= since)
            .group_by(AIObservabilityEvent.user_id)
        )).all()
    return rows


async def _update_module_status(status: str, error: str = None, model_version: str = None):
    from app.database import AsyncSessionLocal
    from app.models.domain import MLModuleConfig
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        config = (await db.execute(
            select(MLModuleConfig).where(MLModuleConfig.module_id == "SECURITY_ANOMALY")
        )).scalar_one_or_none()

        if config:
            config.training_status = status
            config.training_error = error
            if model_version:
                config.model_version = model_version
                config.last_trained_at = datetime.now(timezone.utc)
            await db.commit()


async def _train():
    import pandas as pd
    import numpy as np

    logger.info("Démarrage de l'entraînement du modèle d'anomalie IA")
    await _update_module_status("training")

    try:
        rows = await _load_behavior_data()

        if len(rows) < MIN_SAMPLES:
            msg = f"Données insuffisantes : {len(rows)} utilisateurs (minimum: {MIN_SAMPLES})"
            logger.warning(msg)
            await _update_module_status("error", error=msg)
            return

        # Préparer la matrice de features
        data = []
        for row in rows:
            error_rate = (row.error_count or 0) / max(row.request_count or 1, 1)
            data.append([
                float(row.total_tokens or 0),
                float(row.request_count or 0),
                float(error_rate),
                0.0,  # has_suspicious_hour_activity (simplifié ici)
                float(row.avg_duration_ms or 0),
            ])

        X = np.array(data)

        # Récupérer les params depuis MLModuleConfig
        from app.database import AsyncSessionLocal
        from app.models.domain import MLModuleConfig
        from sqlalchemy import select

        ml_params = {}
        async with AsyncSessionLocal() as db:
            config = (await db.execute(
                select(MLModuleConfig).where(MLModuleConfig.module_id == "SECURITY_ANOMALY")
            )).scalar_one_or_none()
            if config:
                ml_params = config.ml_params or {}

        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = IsolationForest(
            n_estimators=int(ml_params.get("n_estimators", 100)),
            contamination=float(ml_params.get("contamination", 0.05)),
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_scaled)

        # Sauvegarder scaler + model ensemble dans MinIO
        from minio import Minio
        from app.config import settings
        import joblib

        pipeline_bundle = {"scaler": scaler, "model": model}

        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )

        if not client.bucket_exists(MODEL_BUCKET):
            client.make_bucket(MODEL_BUCKET)

        buf = io.BytesIO()
        joblib.dump(pipeline_bundle, buf)
        buf.seek(0)
        client.put_object(MODEL_BUCKET, MODEL_KEY, buf, buf.getbuffer().nbytes)

        version = f"isof_v{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        logger.info(f"Modèle Isolation Forest sauvegardé : {MODEL_BUCKET}/{MODEL_KEY} ({version})")
        await _update_module_status("ready", model_version=version)

        # Recharger en mémoire
        from app.services.security_anomaly_service import security_anomaly_service
        security_anomaly_service.model = model
        logger.info("Modèle Isolation Forest rechargé en mémoire")

    except Exception as e:
        logger.error(f"Erreur entraînement anomalie : {e}")
        await _update_module_status("error", error=str(e))


def train_anomaly_model_task():
    """Point d'entrée pour BackgroundTasks FastAPI."""
    asyncio.run(_train())
