import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.domain import Employee, ProjectAssignment, TrainingEnrollment
from app.schemas.prediction import (
    RiskScoreResponse, TurnoverProjectionResponse, MonthProjection,
    SimulationRequest, SimulationResponse
)
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_any_role
from app.services.field_access_service import apply_field_access, get_primary_role
from app.services.current_employee_service import get_or_create_current_employee
from app.services.hr_analytics_service import build_turnover_projection
from app.services.prediction_scoring_service import calculate_and_store_risk_score, get_risk_score_payload

router = APIRouter(prefix="/predict", tags=["Predictions"])
logger = logging.getLogger(__name__)

# Dépendances RBAC
risk_roles = require_any_role("manager", "hr", "director")
team_risk_roles = require_any_role("manager", "hr")
turnover_roles = require_any_role("hr", "director")
simulate_roles = require_any_role("director", "hr")


@router.get("/risk/{employee_id}", response_model=RiskScoreResponse, dependencies=[Depends(risk_roles)])
async def get_employee_risk(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Score de désengagement d'un employé"""

    employee = (
        await db.execute(
            select(Employee).options(
                selectinload(Employee.department),
                selectinload(Employee.job),
                selectinload(Employee.tasks),
                selectinload(Employee.attendances),
                selectinload(Employee.contracts),
                selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
                selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
                selectinload(Employee.engagement_snapshots),
            ).where(Employee.id == employee_id)
        )
    ).scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé introuvable.")

    if "hr" not in current_user.roles and "director" not in current_user.roles:
        manager = await get_or_create_current_employee(current_user, db)
        if employee.manager_id != manager.id:
            raise HTTPException(status_code=403, detail="Cet employé n'est pas dans votre équipe.")

    payload = await calculate_and_store_risk_score(db, employee)
    filtered, field_visibility = await apply_field_access(
        db,
        resource="prediction",
        scope="risk",
        payload=payload,
        role=get_primary_role(current_user.roles),
        context={},
    )
    return RiskScoreResponse(**filtered, field_visibility=field_visibility)

@router.get("/risk", response_model=List[RiskScoreResponse], dependencies=[Depends(team_risk_roles)])
async def get_team_risks(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Scores pour toute l'équipe/tous les employés"""
    query = select(Employee).options(
        selectinload(Employee.department),
        selectinload(Employee.job),
        selectinload(Employee.tasks),
        selectinload(Employee.attendances),
        selectinload(Employee.contracts),
        selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
        selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
        selectinload(Employee.engagement_snapshots),
    )

    if "hr" not in current_user.roles:
        manager = await get_or_create_current_employee(current_user, db)
        query = query.where(Employee.manager_id == manager.id)

    employees = (await db.execute(query)).scalars().all()
    responses = []
    for employee in employees:
        payload = await calculate_and_store_risk_score(db, employee)
        filtered, field_visibility = await apply_field_access(
            db,
            resource="prediction",
            scope="risk",
            payload=payload,
            role=get_primary_role(current_user.roles),
            context={},
        )
        responses.append(RiskScoreResponse(**filtered, field_visibility=field_visibility))
    return responses

@router.get("/turnover", response_model=TurnoverProjectionResponse, dependencies=[Depends(turnover_roles)])
async def get_turnover_projection(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Projection turnover à 6 mois"""
    employees = (
        await db.execute(
            select(Employee).options(
                selectinload(Employee.department),
                selectinload(Employee.tasks),
                selectinload(Employee.attendances),
                selectinload(Employee.contracts),
                selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
                selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
                selectinload(Employee.engagement_snapshots),
            )
        )
    ).scalars().all()
    risk_scores = [round(get_risk_score_payload(employee)["score"]) for employee in employees if employee.status != "inactif"]
    monthly_scores = risk_scores[:6] if len(risk_scores) >= 6 else risk_scores + [max(22, round(sum(risk_scores) / len(risk_scores))) if risk_scores else 28] * max(0, 6 - len(risk_scores))
    payload = {
        "months": [MonthProjection(**month) for month in build_turnover_projection(monthly_scores[:6], len(employees))],
        "summary": f"Projection consolidée sur 6 mois calculée à partir des signaux RH réels de {len(employees)} collaborateurs.",
    }
    filtered, field_visibility = await apply_field_access(
        db,
        resource="prediction",
        scope="turnover",
        payload=payload,
        role=get_primary_role(current_user.roles),
        context={},
    )
    return TurnoverProjectionResponse(**filtered, field_visibility=field_visibility)

@router.post("/simulate", response_model=SimulationResponse, dependencies=[Depends(simulate_roles)])
async def simulate_scenario(
    request: SimulationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Simulation scénario (ex: +5% salaire)"""
    logger.info(f"Simulation demandée : {request.scenario_type} avec params {request.parameters}")
    employees = (
        await db.execute(
            select(Employee).options(
                selectinload(Employee.department),
                selectinload(Employee.job),
                selectinload(Employee.tasks),
                selectinload(Employee.attendances),
                selectinload(Employee.contracts),
                selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
                selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
                selectinload(Employee.engagement_snapshots),
            )
        )
    ).scalars().all()
    active_employees = [employee for employee in employees if employee.status != "inactif"]
    baseline_payloads = [get_risk_score_payload(employee) for employee in active_employees]
    baseline_scores = [p["score"] for p in baseline_payloads]
    baseline_turnover = round(sum(baseline_scores) / len(baseline_scores) / 10, 1) if baseline_scores else 4.2
    baseline_engagement = round(
        sum(p["engagement"] for p in baseline_payloads) / len(active_employees),
        1,
    ) if active_employees else 72.0
    active_contract_salaries = [
        contract.salary
        for employee in active_employees
        for contract in employee.contracts
        if contract.is_active and contract.salary is not None
    ]
    average_salary = round(sum(active_contract_salaries) / len(active_contract_salaries), 2) if active_contract_salaries else 42000.0
    raise_pct = float(request.parameters.get("raise_pct", 0))
    training_pct = float(request.parameters.get("training_pct", 0))
    recognition_pct = float(request.parameters.get("recognition_pct", 0))
    remote_days = float(request.parameters.get("remote_days", 0))
    impact_gain = round((raise_pct * 0.16) + (training_pct * 0.09) + (recognition_pct * 0.08) + (remote_days * 0.42), 1)
    projected_turnover_change = round(max(-6.0, -(impact_gain * 0.28)), 1)
    projected_turnover = round(max(0, baseline_turnover + projected_turnover_change), 1)
    projected_engagement = round(min(96.0, baseline_engagement + impact_gain), 1)
    implementation_cost = round(
        (average_salary * (raise_pct / 100) * len(active_employees))
        + (training_pct * 35 * len(active_employees))
        + (recognition_pct * 12 * len(active_employees))
        + (remote_days * 180 * len(active_employees)),
        2,
    )
    avoided_departures = max(1, round(abs(projected_turnover_change) * len(active_employees) * 0.012))
    average_departure_cost = average_salary * 0.35
    savings = round((avoided_departures * average_departure_cost) / 1000, 1)
    net = round(savings - (implementation_cost / 1000), 1)
    roi = round(savings / max(implementation_cost / 1000, 1), 1) if implementation_cost > 0 else None
    projection = []
    for index, month in enumerate(["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"], start=1):
        ratio = index / 6
        projection.append(
            {
                "month": month,
                "actuel": round(baseline_engagement, 1),
                "projeté": round(baseline_engagement + impact_gain * ratio, 1),
            }
        )
    payload = {
        "impact_description": f"Le scénario '{request.scenario_type}' ferait évoluer le turnover projeté de {baseline_turnover}% vers {projected_turnover:.1f}% en améliorant surtout l'engagement, la formation et la qualité d'intégration.",
        "projected_turnover_change": projected_turnover_change,
        "engagement": projected_engagement,
        "engagement_gain": impact_gain,
        "turnover": projected_turnover,
        "savings": savings,
        "cost": round(implementation_cost / 1000, 1),
        "net": net,
        "roi": roi,
        "projection": projection,
    }
    filtered, field_visibility = await apply_field_access(
        db,
        resource="prediction",
        scope="simulation",
        payload=payload,
        role=get_primary_role(current_user.roles),
        context={},
    )
    return SimulationResponse(**filtered, field_visibility=field_visibility)
