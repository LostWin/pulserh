from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_any_role
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Employee, Interview
from app.routers.dashboard import _get_current_employee
from app.schemas.auth import CurrentUser
from app.schemas.interview import InterviewCreate, InterviewItem, InterviewOverview, InterviewUpdate
from app.schemas.talent_insights import InterviewSummaryPayload
from app.services.audit_service import log_audit

router = APIRouter(prefix="/interviews", tags=["Interviews"])
manager_roles = require_any_role("manager", "hr")


@router.get("", response_model=InterviewOverview, dependencies=[Depends(manager_roles)])
async def list_interviews(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    query = (
        select(Interview)
        .options(selectinload(Interview.employee))
        .order_by(Interview.scheduled_at.asc())
    )
    if "hr" not in current_user.roles:
        query = query.filter(Interview.manager_id == manager.id)
    result = await db.execute(query)
    interviews = result.scalars().all()
    items = [
        InterviewItem(
            id=item.id,
            collaborator_id=item.employee_id,
            collaborator=f"{item.employee.first_name} {item.employee.last_name}",
            date=item.scheduled_at.strftime("%d %B %Y"),
        time=item.scheduled_at.strftime("%H:%M"),
        status=item.status,
        title=item.title,
        interview_type=item.interview_type,
        location=item.location,
        notes=item.notes,
        duration_minutes=item.duration_minutes,
        outcome=item.outcome,
        summary=item.summary,
        next_actions=item.next_actions or [],
    )
        for item in interviews
    ]
    return InterviewOverview(
        items=items,
        planned_count=sum(1 for item in interviews if item.status == "Planifié"),
        pending_count=sum(1 for item in interviews if item.status == "À planifier"),
        average_duration_minutes=45,
    )


@router.post("", response_model=InterviewItem, dependencies=[Depends(manager_roles)])
async def create_interview(
    payload: InterviewCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    employee_result = await db.execute(
        select(Employee).options(selectinload(Employee.manager)).where(Employee.id == payload.employee_id)
    )
    employee = employee_result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Collaborateur introuvable.")
    if "hr" not in current_user.roles and employee.manager_id != manager.id:
        raise HTTPException(status_code=403, detail="Ce collaborateur n'est pas dans votre équipe.")

    scheduled_at = datetime.fromisoformat(payload.scheduled_at)
    interview = Interview(
        employee_id=employee.id,
        manager_id=employee.manager_id or manager.id,
        title=payload.title,
        interview_type=payload.interview_type,
        scheduled_at=scheduled_at.astimezone(timezone.utc) if scheduled_at.tzinfo else scheduled_at.replace(tzinfo=timezone.utc),
        status="Planifié",
        location=payload.location,
        notes=payload.notes,
        duration_minutes=payload.duration_minutes,
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    await log_audit(
        db, current_user.email,
        f"Planification entretien '{interview.interview_type}' avec {employee.first_name} {employee.last_name} le {interview.scheduled_at.strftime('%d/%m/%Y %H:%M')}",
        "hr_action",
        details={"interview_id": interview.id, "employee_id": employee.id, "interview_type": interview.interview_type, "scheduled_at": interview.scheduled_at.isoformat()},
    )
    return InterviewItem(
        id=interview.id,
        collaborator_id=employee.id,
        collaborator=f"{employee.first_name} {employee.last_name}",
        date=interview.scheduled_at.strftime("%d %B %Y"),
        time=interview.scheduled_at.strftime("%H:%M"),
        status=interview.status,
        title=interview.title,
        interview_type=interview.interview_type,
        location=interview.location,
        notes=interview.notes,
        duration_minutes=interview.duration_minutes,
        outcome=interview.outcome,
        summary=interview.summary,
        next_actions=interview.next_actions or [],
    )


@router.put("/{interview_id}", response_model=InterviewItem, dependencies=[Depends(manager_roles)])
async def update_interview(
    interview_id: str,
    payload: InterviewUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    result = await db.execute(
        select(Interview).options(selectinload(Interview.employee)).where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Entretien introuvable.")
    if "hr" not in current_user.roles and interview.manager_id != manager.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas modifier cet entretien.")

    if payload.scheduled_at:
        scheduled_at = datetime.fromisoformat(payload.scheduled_at)
        interview.scheduled_at = scheduled_at.astimezone(timezone.utc) if scheduled_at.tzinfo else scheduled_at.replace(tzinfo=timezone.utc)
    if payload.title is not None:
        interview.title = payload.title
    if payload.interview_type is not None:
        interview.interview_type = payload.interview_type
    if payload.location is not None:
        interview.location = payload.location
    if payload.notes is not None:
        interview.notes = payload.notes
    if payload.status is not None:
        interview.status = payload.status
    if payload.duration_minutes is not None:
        interview.duration_minutes = payload.duration_minutes
    if payload.outcome is not None:
        interview.outcome = payload.outcome
    if payload.summary is not None:
        interview.summary = payload.summary
    if payload.next_actions is not None:
        interview.next_actions = payload.next_actions

    await db.commit()
    await db.refresh(interview)
    await log_audit(
        db, current_user.email,
        f"Modification entretien {interview_id} (statut: {payload.status or interview.status})",
        "hr_action",
        details={"interview_id": interview_id, "employee_id": interview.employee_id, "status": payload.status},
    )
    return InterviewItem(
        id=interview.id,
        collaborator_id=interview.employee_id,
        collaborator=f"{interview.employee.first_name} {interview.employee.last_name}",
        date=interview.scheduled_at.strftime("%d %B %Y"),
        time=interview.scheduled_at.strftime("%H:%M"),
        status=interview.status,
        title=interview.title,
        interview_type=interview.interview_type,
        location=interview.location,
        notes=interview.notes,
        duration_minutes=interview.duration_minutes,
        outcome=interview.outcome,
        summary=interview.summary,
        next_actions=interview.next_actions or [],
    )


@router.post("/{interview_id}/summary", response_model=InterviewItem, dependencies=[Depends(manager_roles)])
async def save_interview_summary(
    interview_id: str,
    payload: InterviewSummaryPayload,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    result = await db.execute(
        select(Interview).options(selectinload(Interview.employee)).where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Entretien introuvable.")
    if "hr" not in current_user.roles and interview.manager_id != manager.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas enrichir cet entretien.")

    if payload.outcome is not None:
        interview.outcome = payload.outcome
    if payload.summary is not None:
        interview.summary = payload.summary
    interview.next_actions = payload.next_actions
    if interview.status == "Planifié":
        interview.status = "Complété"

    await db.commit()
    await db.refresh(interview)
    await log_audit(
        db, current_user.email,
        f"Création compte-rendu entretien {interview_id} (statut: {interview.status})",
        "hr_action",
        details={"interview_id": interview_id, "employee_id": interview.employee_id, "outcome": payload.outcome},
    )
    return InterviewItem(
        id=interview.id,
        collaborator_id=interview.employee_id,
        collaborator=f"{interview.employee.first_name} {interview.employee.last_name}",
        date=interview.scheduled_at.strftime("%d %B %Y"),
        time=interview.scheduled_at.strftime("%H:%M"),
        status=interview.status,
        title=interview.title,
        interview_type=interview.interview_type,
        location=interview.location,
        notes=interview.notes,
        duration_minutes=interview.duration_minutes,
        outcome=interview.outcome,
        summary=interview.summary,
        next_actions=interview.next_actions or [],
    )


@router.delete("/{interview_id}", dependencies=[Depends(manager_roles)])
async def cancel_interview(
    interview_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    interview = await db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Entretien introuvable.")
    if "hr" not in current_user.roles and interview.manager_id != manager.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas annuler cet entretien.")

    interview.status = "Annulé"
    await db.commit()
    await log_audit(
        db, current_user.email,
        f"Annulation entretien {interview_id}",
        "hr_action",
        details={"interview_id": interview_id, "employee_id": interview.employee_id},
    )
    return {"status": "cancelled", "id": interview_id}
