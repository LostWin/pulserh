"""
Tâche d'entraînement du modèle d'absentéisme (Prophet).

Agrège les données d'absence par jour (tous départements confondus),
entraîne un modèle Prophet et le sauvegarde dans MinIO.
Met à jour le statut d'entraînement dans MLModuleConfig.
"""
import asyncio
import io
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

MODEL_BUCKET = "ml-models"
MODEL_KEY = "absenteeism_prophet_v1.pkl"
MIN_SAMPLES = 30  # Minimum de jours d'historique


async def _load_absence_series():
    """Charge la série temporelle d'absences agrégée par jour."""
    from app.database import AsyncSessionLocal
    from app.models.domain import Attendance
    from sqlalchemy import select, func

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(
                Attendance.date.label("ds"),
                func.count().label("y")
            )
            .where(Attendance.status == "Absent")
            .group_by(Attendance.date)
            .order_by(Attendance.date)
        )).all()
    return rows


async def _update_module_status(status: str, error: str = None, model_version: str = None):
    """Met à jour le statut d'entraînement dans la base de données."""
    from app.database import AsyncSessionLocal
    from app.models.domain import MLModuleConfig
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        config = (await db.execute(
            select(MLModuleConfig).where(MLModuleConfig.module_id == "ABSENTEEISM")
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

    logger.info("Démarrage de l'entraînement du modèle d'absentéisme")
    await _update_module_status("training")

    try:
        rows = await _load_absence_series()

        if len(rows) < MIN_SAMPLES:
            msg = f"Données insuffisantes : {len(rows)} jours (minimum: {MIN_SAMPLES})"
            logger.warning(msg)
            await _update_module_status("error", error=msg)
            return

        df = pd.DataFrame(rows, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"])

        try:
            from prophet import Prophet
        except ImportError:
            from fbprophet import Prophet

        model = Prophet(
            seasonality_mode="additive",
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
        )
        model.fit(df)

        # Sauvegarder dans MinIO
        from minio import Minio
        from app.config import settings
        import joblib

        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )

        if not client.bucket_exists(MODEL_BUCKET):
            client.make_bucket(MODEL_BUCKET)

        buf = io.BytesIO()
        joblib.dump(model, buf)
        buf.seek(0)
        client.put_object(MODEL_BUCKET, MODEL_KEY, buf, buf.getbuffer().nbytes)

        version = f"prophet_v{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        logger.info(f"Modèle Prophet sauvegardé : {MODEL_BUCKET}/{MODEL_KEY} ({version})")
        await _update_module_status("ready", model_version=version)

        # Recharger en mémoire
        from app.services.absenteeism_service import absenteeism_service
        absenteeism_service.model = model
        logger.info("Modèle Prophet rechargé en mémoire")

    except Exception as e:
        logger.error(f"Erreur entraînement absentéisme : {e}")
        await _update_module_status("error", error=str(e))


async def train_absenteeism_model_task():
    """Point d'entrée pour BackgroundTasks FastAPI."""
    await _train()
