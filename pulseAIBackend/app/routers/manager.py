import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_any_role
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Employee, PerformanceObjective, Interview
from app.routers.dashboard import _get_current_employee
from app.schemas.auth import CurrentUser
from app.schemas.manager import ObjectiveCreate, ObjectiveUpdate, ObjectiveResponse, AutoScheduleRequest, TeamVibeResponse
from app.services.calendar_connector import calendar_connector
from app.services.hr_analytics_service import employee_risk_payload

router = APIRouter(prefix="/manager", tags=["Manager V2"])
manager_roles = require_any_role("manager", "hr")
logger = logging.getLogger(__name__)

# --- Objectifs ---

@router.get("/objectives", response_model=list[ObjectiveResponse], dependencies=[Depends(manager_roles)])
async def get_team_objectives(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    query = select(PerformanceObjective).join(Employee, PerformanceObjective.employee_id == Employee.id)
    if "hr" not in current_user.roles:
        query = query.where(Employee.manager_id == manager.id)
    
    result = await db.execute(query)
    objectives = result.scalars().all()
    return objectives

@router.post("/objectives", response_model=ObjectiveResponse, dependencies=[Depends(manager_roles)])
async def create_objective(
    payload: ObjectiveCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    
    # Verify employee is in team
    employee = await db.get(Employee, payload.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Collaborateur introuvable.")
    if "hr" not in current_user.roles and employee.manager_id != manager.id:
        raise HTTPException(status_code=403, detail="Collaborateur non membre de votre équipe.")

    objective = PerformanceObjective(
        employee_id=employee.id,
        owner_id=manager.id,
        title=payload.title,
        description=payload.description,
        target_date=payload.target_date,
        status="planned",
        progress_pct=0
    )
    db.add(objective)
    await db.commit()
    await db.refresh(objective)
    return objective

@router.put("/objectives/{objective_id}", response_model=ObjectiveResponse, dependencies=[Depends(manager_roles)])
async def update_objective(
    objective_id: str,
    payload: ObjectiveUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    objective = await db.get(PerformanceObjective, objective_id)
    if not objective:
        raise HTTPException(status_code=404, detail="Objectif introuvable.")
        
    employee = await db.get(Employee, objective.employee_id)
    if "hr" not in current_user.roles and employee.manager_id != manager.id:
        raise HTTPException(status_code=403, detail="Opération non autorisée sur cet objectif.")

    if payload.title is not None:
        objective.title = payload.title
    if payload.description is not None:
        objective.description = payload.description
    if payload.status is not None:
        objective.status = payload.status
    if payload.progress_pct is not None:
        objective.progress_pct = payload.progress_pct
    if payload.target_date is not None:
        objective.target_date = payload.target_date
        
    await db.commit()
    await db.refresh(objective)
    return objective

# --- Auto-Scheduling 1:1 ---

@router.post("/interviews/auto-schedule", dependencies=[Depends(manager_roles)])
async def auto_schedule_1_1(
    payload: AutoScheduleRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    employee = await db.get(Employee, payload.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Collaborateur introuvable.")
    if "hr" not in current_user.roles and employee.manager_id != manager.id:
        raise HTTPException(status_code=403, detail="Collaborateur non membre de votre équipe.")

    # Suggérer des créneaux
    slots = await calendar_connector.suggest_slots(db, manager.id)
    best_slot = slots[0] if slots else datetime.now(timezone.utc) + timedelta(days=2)
    
    interview = Interview(
        employee_id=employee.id,
        manager_id=manager.id,
        title=payload.title,
        interview_type=payload.interview_type,
        scheduled_at=best_slot,
        status="Planifié",
        duration_minutes=payload.duration_minutes
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    
    return {
        "status": "scheduled",
        "interview_id": interview.id,
        "scheduled_at": interview.scheduled_at.isoformat()
    }

# --- Team Vibe ---

@router.get("/vibe", response_model=TeamVibeResponse, dependencies=[Depends(manager_roles)])
async def get_team_vibe(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    
    team_result = await db.execute(
        select(Employee).options(
            selectinload(Employee.tasks),
            selectinload(Employee.attendances),
            selectinload(Employee.engagement_snapshots)
        ).filter(Employee.manager_id == manager.id)
    )
    team = team_result.scalars().all()
    
    if not team:
        return TeamVibeResponse(
            team_size=0,
            avg_engagement=0,
            at_risk_count=0,
            overall_vibe_score=0,
            summary_message="Votre équipe est vide.",
            recommended_actions=[]
        )
        
    team_payload = [employee_risk_payload(emp) for emp in team]
    avg_engagement = round(sum(p["engagement"] for p in team_payload) / len(team_payload))
    at_risk = sum(1 for p in team_payload if p["level"] in ["orange", "red"])
    
    # Calcul de la vibe
    vibe_score = avg_engagement - (at_risk * 5)
    vibe_score = max(0, min(100, vibe_score))
    
    if vibe_score >= 80:
        summary_message = "Excellente dynamique d'équipe."
        recommended_actions = ["Féliciter l'équipe pour ses efforts", "Identifier des opportunités de mentorat"]
    elif vibe_score >= 60:
        summary_message = "Dynamique stable avec des points de friction mineurs."
        recommended_actions = ["Vérifier la répartition de la charge", "Planifier des 1:1 réguliers"]
    else:
        summary_message = "Signaux de démotivation ou surcharge détectés."
        recommended_actions = ["Mener une session d'écoute active", "Réduire la pression sur les projets critiques", "Utiliser l'auto-scheduling pour des entretiens rapides"]
        
    return TeamVibeResponse(
        team_size=len(team),
        avg_engagement=avg_engagement,
        at_risk_count=at_risk,
        overall_vibe_score=vibe_score,
        summary_message=summary_message,
        recommended_actions=recommended_actions
    )
