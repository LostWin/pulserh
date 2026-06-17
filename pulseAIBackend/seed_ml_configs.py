import asyncio
import uuid
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.domain import MLModuleConfig

MODULES = [
    {
        "module_id": "CHURN_RISK",
        "module_name": "Risque de Départ (Churn)",
        "mode": "heuristic",
        "alert_threshold": 0.70,
        "heuristic_params": {
            "absence_weight": 0.45,
            "sick_leave_weight": 0.30,
            "task_score_weight": 0.25,
        },
        "ml_params": {
            "model_key": "risk_xgboost_v1.pkl",
            "model_bucket": "ml-models",
            "class_weight": "balanced",
            "n_estimators": 200,
            "max_depth": 6,
            "shap_enabled": True,
        },
    },
    {
        "module_id": "ABSENTEEISM",
        "module_name": "Prévision Absentéisme",
        "mode": "heuristic",
        "alert_threshold": 0.60,
        "heuristic_params": {
            "rolling_window_days": 90,
            "threshold_absences": 5,
        },
        "ml_params": {
            "model_type": "prophet",
            "forecast_horizon_days": 30,
            "seasonality_mode": "additive",
            "aggregate_level": "department",
        },
    },
    {
        "module_id": "SENTIMENT",
        "module_name": "Analyse de Sentiment",
        "mode": "heuristic",
        "alert_threshold": 0.50,
        "heuristic_params": {
            "negative_keywords": ["démission", "burn-out", "surcharge", "injuste"],
            "positive_keywords": ["motivation", "excellent", "évolution", "fier"],
        },
        "ml_params": {
            "model_name": "cmarkea/distilcamembert-base-sentiment",
            "anonymize_before_inference": True,
            "aggregate_results": True,
            "pii_entities": ["PER", "EMAIL", "ORG"],
        },
    },
    {
        "module_id": "TRAINING_RECO",
        "module_name": "Recommandation Formations",
        "mode": "heuristic",
        "alert_threshold": 0.65,
        "heuristic_params": {
            "max_recommendations": 3,
            "mandatory_first": True,
        },
        "ml_params": {
            "similarity_metric": "cosine",
            "top_k": 5,
            "cold_start_strategy": "job_rules",
            "collaborative_weight": 0.30,
            "content_weight": 0.70,
        },
    },
    {
        "module_id": "SECURITY_ANOMALY",
        "module_name": "Détection Anomalies IA",
        "mode": "heuristic",
        "alert_threshold": 0.80,
        "heuristic_params": {
            "max_tokens_per_hour": 50000,
            "max_requests_per_hour": 200,
            "suspicious_hours_start": 0,
            "suspicious_hours_end": 5,
        },
        "ml_params": {
            "model_type": "isolation_forest",
            "contamination": 0.05,
            "n_estimators": 100,
            "batch_interval_minutes": 60,
        },
    },
]


async def seed():
    async with AsyncSessionLocal() as session:
        for m in MODULES:
            result = await session.execute(
                select(MLModuleConfig).where(MLModuleConfig.module_id == m["module_id"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                session.add(MLModuleConfig(id=str(uuid.uuid4()), **m))
                print(f"✅ Créé : {m['module_id']}")
            else:
                print(f"⏭️  Déjà existant, ignoré : {m['module_id']}")

        await session.commit()
        print("\n🎉 Seed terminé avec succès !")


if __name__ == "__main__":
    asyncio.run(seed())
