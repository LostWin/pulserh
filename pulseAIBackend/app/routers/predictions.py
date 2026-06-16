import logging
from datetime import datetime, date, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_any_role
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Employee
from app.schemas.auth import CurrentUser
from app.schemas.prediction import (
    MonthProjection, RiskActionsResponse, RiskDetailsResponse,
    RiskScoreResponse, SimulationRequest, SimulationResponse,
    TurnoverProjectionResponse,
)
from app.services.feature_extractor import feature_extractor
from app.services.llm_client import llm_client
from app.services.risk_predictor import risk_predictor

router = APIRouter(prefix="/predict", tags=["Predictions"])
logger = logging.getLogger(__name__)

risk_roles = require_any_role("manager", "hr", "director")
team_roles = require_any_role("manager", "hr")
turnover_roles = require_any_role("hr", "director")
simulate_roles = require_any_role("director", "hr")


def _parse_result(result: dict) -> RiskScoreResponse:
    return RiskScoreResponse(
        employee_id=result["employee_id"],
        score=result["score"],
        level=result["level"],
        computed_at=datetime.fromisoformat(result["computed_at"]),
    )


@router.get(
    "/risk/{employee_id}",
    response_model=RiskScoreResponse,
    summary="Score de désengagement d'un employé",
)
async def get_employee_risk(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(risk_roles),
):
    """
    Retourne le score de risque de départ (0–1) et le niveau associé
    (green / orange / red) pour un employé donné.

    Un manager ne peut consulter que les membres de son équipe.
    Le résultat est mis en cache Redis pendant 1 heure.
    """
    if "hr" not in current_user.roles and "director" not in current_user.roles:
        emp = (await db.execute(
            select(Employee).where(
                Employee.id == employee_id,
                Employee.manager_id == current_user.id,
            )
        )).scalar_one_or_none()
        if not emp:
            raise HTTPException(status_code=403, detail="Cet employé n'est pas dans votre équipe.")

    try:
        return _parse_result(await risk_predictor.predict(employee_id, db))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/risk/{employee_id}/details",
    response_model=RiskDetailsResponse,
    summary="Détail des signaux faibles d'un employé",
)
async def get_employee_risk_details(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(team_roles),
):
    """
    Retourne le score de risque accompagné des valeurs de features
    utilisées par le modèle (ancienneté, absences, congés maladie, etc.).
    """
    try:
        result = await risk_predictor.predict(employee_id, db)
        features = await feature_extractor.get_employee_features(employee_id, db)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return RiskDetailsResponse(
        employee_id=employee_id,
        score=result["score"],
        level=result["level"],
        features={k: v for k, v in features.items() if k != "employee_id"},
        computed_at=datetime.fromisoformat(result["computed_at"]),
    )


@router.get(
    "/risk/{employee_id}/actions",
    response_model=RiskActionsResponse,
    summary="Plan d'action généré par le LLM pour un employé à risque",
)
async def get_employee_risk_actions(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(team_roles),
):
    """
    Génère 3 actions concrètes via le LLM en s'appuyant sur le score
    de risque et les signaux faibles de l'employé.
    """
    try:
        result = await risk_predictor.predict(employee_id, db)
        features = await feature_extractor.get_employee_features(employee_id, db)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    prompt = (
        f"Un employé présente un score de désengagement de {result['score']:.0%} "
        f"(niveau : {result['level']}).\n"
        f"Signaux observés :\n"
        f"- Ancienneté : {features['tenure_months']} mois\n"
        f"- Absences (3 mois) : {features['absence_count_3m']}\n"
        f"- Retards (3 mois) : {features['late_count_3m']}\n"
        f"- Congés maladie (12 mois) : {features['sick_leave_count_12m']}\n"
        f"- Score moyen sur les tâches : {features['avg_task_score']:.1f}/10\n"
        f"- Tâches en retard : {features['overdue_tasks_count']}\n\n"
        f"Propose 3 actions concrètes que le manager peut mettre en place "
        f"pour retenir cet employé. Réponds uniquement avec une liste numérotée."
    )

    try:
        response = await llm_client.generate(prompt, temperature=0.4, max_tokens=400)
        actions = [
            line.strip()
            for line in response.strip().split("\n")
            if line.strip() and line.strip()[0].isdigit()
        ]
    except Exception as e:
        logger.error(f"Erreur LLM pour les actions de risque : {e}")
        actions = [
            "Organiser un entretien individuel",
            "Évaluer la charge de travail",
            "Proposer une formation adaptée",
        ]

    return RiskActionsResponse(
        employee_id=employee_id,
        level=result["level"],
        actions=actions,
    )


@router.get(
    "/risk",
    response_model=List[RiskScoreResponse],
    summary="Scores de risque pour l'ensemble de l'équipe",
)
async def get_team_risks(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(team_roles),
):
    """
    Retourne les scores de risque pour tous les employés accessibles
    par l'utilisateur connecté (équipe du manager, ou tous les employés pour RH).
    """
    query = select(Employee.id)
    if "manager" in current_user.roles and "hr" not in current_user.roles:
        query = query.where(Employee.manager_id == current_user.id)

    employee_ids = (await db.execute(query)).scalars().all()

    scores = []
    for emp_id in employee_ids:
        try:
            scores.append(_parse_result(await risk_predictor.predict(emp_id, db)))
        except Exception:
            continue

    return scores


@router.get(
    "/turnover",
    response_model=TurnoverProjectionResponse,
    summary="Projection du turnover sur 6 mois",
)
async def get_turnover_projection(
    db: AsyncSession = Depends(get_db),
    _=Depends(turnover_roles),
):
    """
    Calcule le nombre d'employés à risque élevé (rouge) et projette
    les départs probables sur les 6 prochains mois.
    """
    employee_ids = (await db.execute(select(Employee.id))).scalars().all()

    high_risk = 0
    for emp_id in employee_ids:
        try:
            r = await risk_predictor.predict(emp_id, db)
            if r["level"] == "red":
                high_risk += 1
        except Exception:
            continue

    today = date.today()
    months = []
    for i in range(1, 7):
        m = (today.month - 1 + i) % 12 + 1
        y = today.year + (today.month - 1 + i) // 12
        confidence = round(max(0.5, 0.9 - i * 0.07), 2)
        projected = max(0, round(high_risk * (1 - i * 0.1) * confidence))
        months.append(MonthProjection(
            month=f"{y:04d}-{m:02d}",
            projected_departures=projected,
            confidence=confidence,
        ))

    return TurnoverProjectionResponse(months=months)


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    summary="Simulation d'un scénario RH",
)
async def simulate_scenario(
    request: SimulationRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(simulate_roles),
):
    """
    Modifie les features d'un employé selon un scénario (ex : augmentation salariale)
    et compare le score de risque simulé avec le score actuel.

    Scénarios supportés : `salary_increase` (paramètre `salary_increase_pct`),
    `reduce_overdue`. Tout autre scénario applique les paramètres directement
    comme surcharges de features.
    """
    logger.info(f"Simulation : {request.scenario_type} pour l'employé {request.employee_id}")

    overrides: dict = {}
    if request.scenario_type == "salary_increase":
        pct = request.parameters.get("salary_increase_pct", 0) / 100
        features = await feature_extractor.get_employee_features(request.employee_id, db)
        overrides["salary"] = features["salary"] * (1 + pct)
    elif request.scenario_type == "reduce_overdue":
        overrides["overdue_tasks_count"] = 0
    else:
        overrides = dict(request.parameters)

    try:
        original, simulated = await risk_predictor.predict_with_scenario(
            request.employee_id, overrides, db
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    delta = simulated - original
    direction = "réduire" if delta < 0 else "augmenter"

    return SimulationResponse(
        original_score=original,
        simulated_score=simulated,
        projected_turnover_change=round(delta * 100, 2),
        impact_description=(
            f"Le scénario '{request.scenario_type}' devrait {direction} "
            f"le risque de départ de {abs(delta):.0%}."
        ),
    )
