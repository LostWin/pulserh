from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.domain import Employee, PredictionSnapshot
from app.services.prediction_feature_service import extract_employee_features
from app.services.prediction_explainability_service import explain_risk_score
from app.services.hr_analytics_service import employee_tenure_label
from app.config import settings

# =====================================================================
# HEURISTIQUES DE SCORING IA
# =====================================================================
# Ces constantes définissent les poids et multiplicateurs utilisés pour
# évaluer le risque de départ/désengagement d'un collaborateur.

# Charge de travail : Base 24, +18 par tâche en retard, +4 par projet actif
WORKLOAD_BASE = 24
WORKLOAD_OVERDUE_TASK_WEIGHT = 18
WORKLOAD_ACTIVE_PROJECT_WEIGHT = 4

# Assiduité : Base 18, +17 par absence sur les 30 derniers jours
ATTENDANCE_BASE = 18
ATTENDANCE_ABSENCE_WEIGHT = 17

# Formation obligatoire : Base 15, +22 par formation obligatoire en retard
TRAINING_MANDATORY_BASE = 15
TRAINING_OVERDUE_WEIGHT = 22

# Reconnaissance / progression : Base 28, +9 par formation manquante (sur un objectif de 3)
RECOGNITION_BASE = 28
RECOGNITION_MISSING_TRAINING_WEIGHT = 9

# Plafond global pour chaque facteur de risque
MAX_FACTOR_SCORE = 95

def get_risk_score_payload(employee: Employee) -> dict:
    features = extract_employee_features(employee)
    
    factors = [
        {"label": "Charge de travail", "value": min(MAX_FACTOR_SCORE, WORKLOAD_BASE + features["overdue_tasks"] * WORKLOAD_OVERDUE_TASK_WEIGHT + features["active_projects"] * WORKLOAD_ACTIVE_PROJECT_WEIGHT)},
        {"label": "Assiduité", "value": min(MAX_FACTOR_SCORE, ATTENDANCE_BASE + features["absences_30"] * ATTENDANCE_ABSENCE_WEIGHT)},
        {"label": "Formation obligatoire", "value": min(MAX_FACTOR_SCORE, TRAINING_MANDATORY_BASE + features["mandatory_training_overdue"] * TRAINING_OVERDUE_WEIGHT)},
        {"label": "Engagement déclaré", "value": min(MAX_FACTOR_SCORE, max(10, 100 - features["engagement_score"]))},
        {"label": "Reconnaissance / progression", "value": min(MAX_FACTOR_SCORE, RECOGNITION_BASE + max(0, 3 - features["training_completed"]) * RECOGNITION_MISSING_TRAINING_WEIGHT)},
    ]
    
    top_factors, level, recommendation = explain_risk_score(factors)
    score = round(sum(item["value"] for item in top_factors) / len(top_factors))
    
    return {
        "employee_id": employee.id,
        "employee_name": f"{employee.first_name} {employee.last_name}",
        "department": employee.department.name if employee.department else "Non assigné",
        "title": employee.job.title if employee.job else "Collaborateur",
        "tenure": employee_tenure_label(employee),
        "score": float(score),
        "level": level,
        "recommendation": recommendation,
        "factors": top_factors,
        "computed_at": datetime.now(timezone.utc),
        "engagement": features["engagement_score"],
    }

async def calculate_and_store_risk_score(db: AsyncSession, employee: Employee) -> dict:
    payload = get_risk_score_payload(employee)
    
    # Historisation
    snapshot = PredictionSnapshot(
        employee_id=employee.id,
        prediction_type="risk",
        score=payload["score"],
        level=payload["level"],
        factors_json=payload["factors"],
        model_version=settings.PREDICTION_MODEL_VERSION
    )
    db.add(snapshot)
    await db.commit()
    
    return payload
