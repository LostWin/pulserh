import asyncio
import io
import logging
from datetime import datetime, timezone

import joblib
from minio import Minio
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from app.config import settings
from celery_app import celery_app

logger = logging.getLogger(__name__)

MODEL_BUCKET = "ml-models"
MODEL_KEY = "risk_xgboost_v1.pkl"
MIN_SAMPLES = 10


async def _charger_donnees():
    from app.database import AsyncSessionLocal
    from app.services.feature_extractor import feature_extractor
    async with AsyncSessionLocal() as db:
        return await feature_extractor.get_training_data(db)


async def _update_module_status(status: str, error: str = None, model_version: str = None):
    """Met à jour le statut d'entraînement dans la base de données."""
    from app.database import AsyncSessionLocal
    from app.models.domain import MLModuleConfig
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        config = (await db.execute(
            select(MLModuleConfig).where(MLModuleConfig.module_id == "CHURN_RISK")
        )).scalar_one_or_none()

        if config:
            config.training_status = status
            config.training_error = error
            if model_version:
                config.model_version = model_version
                config.last_trained_at = datetime.now(timezone.utc)
            await db.commit()


def _minio() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )


async def _run_training():
    """Logique principale d'entraînement (réutilisable depuis Celery ou BackgroundTasks)."""
    logger.info("Démarrage de l'entraînement du modèle de risque de départ")
    await _update_module_status("training")

    try:
        df = await _charger_donnees()

        if len(df) < MIN_SAMPLES:
            msg = f"Entraînement annulé : seulement {len(df)} échantillons disponibles (minimum: {MIN_SAMPLES})"
            logger.warning(msg)
            await _update_module_status("error", error=msg)
            return

        X = df.drop(columns=["churned"])
        y = df["churned"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
        )

        model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            eval_metric="logloss",
        )
        model.fit(X_train, y_train)

        auc = None
        if y_test.nunique() > 1:
            auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
            logger.info(f"AUC-ROC : {auc:.4f}")

        client = _minio()
        if not client.bucket_exists(MODEL_BUCKET):
            client.make_bucket(MODEL_BUCKET)

        buf = io.BytesIO()
        joblib.dump(model, buf)
        buf.seek(0)
        client.put_object(MODEL_BUCKET, MODEL_KEY, buf, buf.getbuffer().nbytes)

        version = f"xgboost_churn_v{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        logger.info(f"Modèle XGBoost sauvegardé : {MODEL_BUCKET}/{MODEL_KEY} ({version})")
        await _update_module_status("ready", model_version=version)

        # Recharger en mémoire
        from app.services.risk_predictor import risk_predictor
        risk_predictor.model = model
        logger.info("Modèle XGBoost rechargé en mémoire")

    except Exception as e:
        logger.error(f"Erreur entraînement churn : {e}")
        await _update_module_status("error", error=str(e))


@celery_app.task(name="app.tasks.train_risk_model", bind=True)
def train_risk_model(self):
    """Tâche Celery (exécution planifiée)."""
    asyncio.run(_run_training())


def train_risk_model_task():
    """Point d'entrée pour BackgroundTasks FastAPI (exécution à la demande)."""
    asyncio.run(_run_training())

