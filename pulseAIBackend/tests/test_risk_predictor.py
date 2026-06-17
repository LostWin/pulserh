"""Tests unitaires — RiskPredictor."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.services.risk_predictor import RiskPredictor, _level


# ─── Tests _level ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("score,expected", [
    (0.0, "green"),
    (0.32, "green"),
    (0.33, "orange"),
    (0.65, "orange"),
    (0.66, "red"),
    (1.0, "red"),
])
def test_level(score, expected):
    assert _level(score) == expected


# ─── Tests RiskPredictor.load ─────────────────────────────────────────────────

def test_load_modele_absent(caplog):
    """load() log un warning si le modèle est absent de MinIO."""
    from minio.error import S3Error

    predictor = RiskPredictor()
    with patch("app.services.risk_predictor.Minio", create=True) as MockMinio:
        mock_client = MagicMock()
        mock_client.get_object.side_effect = S3Error(
            "NoSuchKey", "The specified key does not exist.",
            "risk_xgboost_v1.pkl", "request-id", "host-id", MagicMock()
        )
        MockMinio.return_value = mock_client

        predictor.load()

    assert predictor.model is None


# ─── Tests RiskPredictor.predict ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_modele_non_charge():
    """predict() utilise le mode heuristique si le mode ML est demandé mais le modèle n'est pas chargé."""
    predictor = RiskPredictor()
    db = AsyncMock()

    # Mock DB return for Employee
    mock_emp = MagicMock()
    mock_emp.id = "emp-1"
    mock_emp.first_name = "Jane"
    mock_emp.last_name = "Doe"
    mock_emp.status = "actif"
    mock_emp.hire_date = None
    mock_emp.engagement_snapshots = []
    mock_emp.tasks = []
    mock_emp.attendances = []
    mock_emp.training_enrollments = []
    mock_emp.project_assignments = []
    mock_emp.department.name = "R&D"
    mock_emp.job.title = "Ingénieur"

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_emp
    db.execute.return_value = mock_res

    # Mock Config to "ml"
    mock_config = MagicMock()
    mock_config.mode = "ml"
    predictor._get_module_config = AsyncMock(return_value=mock_config)

    features = {
        "absence_count_3m": 1,
        "sick_leave_count_12m": 0,
        "avg_task_score": 8.0,
    }

    with patch("app.services.risk_predictor._get_redis", new=AsyncMock(return_value=None)), \
         patch("app.services.risk_predictor.feature_extractor") as mock_fe:
        mock_fe.get_employee_features = AsyncMock(return_value=features)
        result = await predictor.predict("emp-1", db)

    assert result["employee_id"] == "emp-1"
    assert result["mode"] == "heuristic"


@pytest.mark.asyncio
async def test_predict_depuis_cache():
    """predict() retourne le résultat mis en cache sans appeler le modèle."""
    predictor = RiskPredictor()
    predictor.model = MagicMock()  # modèle chargé mais ne doit pas être appelé
    db = AsyncMock()

    cached = json.dumps({
        "employee_id": "emp-1",
        "score": 0.25,
        "level": "green",
        "computed_at": "2025-01-01T00:00:00+00:00",
    })

    mock_redis = AsyncMock()
    mock_redis.get.return_value = cached

    with patch("app.services.risk_predictor._get_redis", return_value=mock_redis):
        result = await predictor.predict("emp-1", db)

    assert result["score"] == 0.25
    assert result["level"] == "green"
    predictor.model.predict_proba.assert_not_called()


@pytest.mark.asyncio
async def test_predict_calcul_et_mise_en_cache():
    """predict() calcule le score et l'écrit dans Redis."""
    predictor = RiskPredictor()

    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])
    predictor.model = mock_model

    db = AsyncMock()

    # Mock DB return for Employee
    mock_emp = MagicMock()
    mock_emp.id = "emp-1"
    mock_emp.first_name = "Jane"
    mock_emp.last_name = "Doe"
    mock_emp.status = "actif"
    mock_emp.hire_date = None
    mock_emp.engagement_snapshots = []
    mock_emp.tasks = []
    mock_emp.attendances = []
    mock_emp.training_enrollments = []
    mock_emp.project_assignments = []
    mock_emp.department.name = "R&D"
    mock_emp.job.title = "Ingénieur"

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_emp
    db.execute.return_value = mock_res

    # Mock Config to "ml"
    mock_config = MagicMock()
    mock_config.mode = "ml"
    predictor._get_module_config = AsyncMock(return_value=mock_config)

    features = {
        "employee_id": "emp-1",
        "tenure_months": 24,
        "salary": 3000.0,
        "contract_type": 0,
        "leave_days_12m": 5,
        "sick_leave_count_12m": 1,
        "absence_count_3m": 0,
        "late_count_3m": 2,
        "avg_task_score": 7.5,
        "overdue_tasks_count": 1,
    }

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # pas en cache

    with patch("app.services.risk_predictor._get_redis", return_value=mock_redis), \
         patch("app.services.risk_predictor.feature_extractor") as mock_fe:
        mock_fe.get_employee_features = AsyncMock(return_value=features)
        result = await predictor.predict("emp-1", db)

    assert result["employee_id"] == "emp-1"
    assert result["score"] == pytest.approx(0.7, abs=0.001)
    assert result["level"] == "red"
    mock_redis.setex.assert_called_once()


# ─── Tests predict_with_scenario ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_with_scenario_salary():
    """predict_with_scenario modifie les features avant la prédiction."""
    predictor = RiskPredictor()

    # Mock Config to "ml"
    mock_config = MagicMock()
    mock_config.mode = "ml"
    predictor._get_module_config = AsyncMock(return_value=mock_config)

    call_count = 0

    def fake_proba(X):
        nonlocal call_count
        call_count += 1
        # Premier appel : score original, second : score simulé
        return np.array([[0.4, 0.6]]) if call_count == 1 else np.array([[0.6, 0.4]])

    mock_model = MagicMock()
    mock_model.predict_proba.side_effect = fake_proba
    predictor.model = mock_model

    db = AsyncMock()
    features = {
        "employee_id": "emp-1",
        "tenure_months": 12,
        "salary": 2500.0,
        "contract_type": 0,
        "leave_days_12m": 3,
        "sick_leave_count_12m": 0,
        "absence_count_3m": 1,
        "late_count_3m": 0,
        "avg_task_score": 8.0,
        "overdue_tasks_count": 0,
    }

    with patch("app.services.risk_predictor.feature_extractor") as mock_fe:
        mock_fe.get_employee_features = AsyncMock(return_value=features)
        original, simulated = await predictor.predict_with_scenario(
            "emp-1", {"salary": 3000.0}, db
        )

    assert original == pytest.approx(0.6, abs=0.001)
    assert simulated == pytest.approx(0.4, abs=0.001)
