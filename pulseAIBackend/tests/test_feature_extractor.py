"""Tests unitaires — FeatureExtractor."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.feature_extractor import CONTRACT_ENCODING, FeatureExtractor


@pytest.fixture
def extractor():
    return FeatureExtractor()


def _make_employee(hire_date=None, status="actif"):
    emp = MagicMock()
    emp.hire_date = hire_date or date(2020, 1, 1)
    emp.status = status
    return emp


def _make_db(employee=None, contract=None, leaves=None, attendances=None, tasks=None):
    """Construit un AsyncSession mocké qui retourne les données fournies."""
    db = AsyncMock()

    async def execute(stmt):
        result = MagicMock()
        # Retourne les données selon l'ordre d'appel
        result.scalar_one_or_none.return_value = employee if employee is not None else None
        result.scalars.return_value.all.return_value = []
        return result

    db.execute = execute
    return db


# ─── Tests CONTRACT_ENCODING ──────────────────────────────────────────────────

def test_contract_encoding_complet():
    assert CONTRACT_ENCODING["CDI"] == 0
    assert CONTRACT_ENCODING["CDD"] == 1
    assert CONTRACT_ENCODING["Alternance"] == 2
    assert CONTRACT_ENCODING["Stage"] == 3


# ─── Tests get_employee_features ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_features_employee_absent(extractor):
    """Lève ValueError si l'employé n'existe pas."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(ValueError, match="introuvable"):
        await extractor.get_employee_features("inexistant", db)


@pytest.mark.asyncio
async def test_features_cles_retournees(extractor):
    """Vérifie que toutes les clés attendues sont présentes."""
    employee = _make_employee(hire_date=date(2021, 6, 1))

    call_count = 0

    async def execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        if call_count == 1:
            # Requête employé
            result.scalar_one_or_none.return_value = employee
        elif call_count == 2:
            # Requête contrat actif
            contract = MagicMock()
            contract.salary = 3500.0
            contract.contract_type = "CDI"
            result.scalar_one_or_none.return_value = contract
        else:
            # Congés, présences, tâches
            result.scalars.return_value.all.return_value = []
            result.scalar_one_or_none.return_value = None
        return result

    db = AsyncMock()
    db.execute = execute

    features = await extractor.get_employee_features("emp-1", db)

    cles_attendues = {
        "employee_id", "tenure_months", "salary", "contract_type",
        "leave_days_12m", "sick_leave_count_12m",
        "absence_count_3m", "late_count_3m",
        "avg_task_score", "overdue_tasks_count",
    }
    assert cles_attendues == set(features.keys())


@pytest.mark.asyncio
async def test_features_anciennete_calcul(extractor):
    """Vérifie le calcul de l'ancienneté en mois."""
    hire = date.today() - timedelta(days=365)
    employee = _make_employee(hire_date=hire)

    call_count = 0

    async def execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        if call_count == 1:
            result.scalar_one_or_none.return_value = employee
        elif call_count == 2:
            result.scalar_one_or_none.return_value = None  # pas de contrat
        else:
            result.scalars.return_value.all.return_value = []
            result.scalar_one_or_none.return_value = None
        return result

    db = AsyncMock()
    db.execute = execute

    features = await extractor.get_employee_features("emp-1", db)
    # ~12 mois, on accepte ±1 mois de marge
    assert 11 <= features["tenure_months"] <= 13


@pytest.mark.asyncio
async def test_features_sans_contrat(extractor):
    """Salary = 0 et contract_type = -1 quand aucun contrat actif."""
    employee = _make_employee()

    call_count = 0

    async def execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        if call_count == 1:
            result.scalar_one_or_none.return_value = employee
        elif call_count == 2:
            result.scalar_one_or_none.return_value = None
        else:
            result.scalars.return_value.all.return_value = []
            result.scalar_one_or_none.return_value = None
        return result

    db = AsyncMock()
    db.execute = execute

    features = await extractor.get_employee_features("emp-1", db)
    assert features["salary"] == 0.0
    assert features["contract_type"] == -1
