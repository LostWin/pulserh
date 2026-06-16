import asyncio
import io
import logging

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


def _minio() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )


@celery_app.task(name="app.tasks.train_risk_model", bind=True)
def train_risk_model(self):
    logger.info("Démarrage de l'entraînement du modèle de risque")

    df = asyncio.run(_charger_donnees())

    if len(df) < MIN_SAMPLES:
        logger.warning(f"Entraînement annulé : seulement {len(df)} échantillons disponibles")
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

    # AUC calculée uniquement si les deux classes sont présentes dans le jeu de test
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

    logger.info(f"Modèle sauvegardé dans {MODEL_BUCKET}/{MODEL_KEY}")
