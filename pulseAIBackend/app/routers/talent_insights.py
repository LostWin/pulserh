from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_any_role
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import (
    Employee,
    EngagementEvent,
    EngagementSnapshot,
    PerformanceObjective,
    PerformanceReview,
    ProjectAssignment,
    TrainingEnrollment,
    Task,
)
from app.schemas.auth import CurrentUser
from app.schemas.talent_insights import (
    EmployeeEngagementResponse,
    EmployeePerformanceResponse,
    EngagementEventItem,
    EngagementSnapshotItem,
    ObjectiveCreatePayload,
    PerformanceObjectiveItem,
    PerformanceReviewItem,
)
from app.services.current_employee_service import get_or_create_current_employee
from app.services.hr_analytics_service import employee_engagement_score, employee_performance_score

router = APIRouter(tags=["Talent Insights"])

read_roles = require_any_role("collaborator", "manager", "hr", "director", "admin")
write_roles = require_any_role("manager", "hr", "admin")


async def _resolve_target_employee(
    employee_id: str,
    current_user: CurrentUser,
    db: AsyncSession,
) -> tuple[Employee, Employee]:
    current_employee = await get_or_create_current_employee(current_user, db)
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.manager),
            selectinload(Employee.attendances),
            selectinload(Employee.tasks).selectinload(Task.project),
            selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
            selectinload(Employee.engagement_snapshots),
        )
        .where(Employee.id == employee_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Collaborateur introuvable.")

    elevated = {"hr", "director", "admin"}
    if elevated & set(current_user.roles):
        return current_employee, target
    if "manager" in current_user.roles and target.manager_id == current_employee.id:
        return current_employee, target
    if "collaborator" in current_user.roles and target.id == current_employee.id:
        return current_employee, target
    raise HTTPException(status_code=403, detail="Accès insuffisant à ce collaborateur.")


@router.get("/employees/{employee_id}/engagement", response_model=EmployeeEngagementResponse, dependencies=[Depends(read_roles)])
async def get_employee_engagement(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, target = await _resolve_target_employee(employee_id, current_user, db)
    snapshots_result = await db.execute(
        select(EngagementSnapshot)
        .where(EngagementSnapshot.employee_id == target.id)
        .order_by(EngagementSnapshot.captured_at.desc())
    )
    snapshots = snapshots_result.scalars().all()
    events_result = await db.execute(
        select(EngagementEvent)
        .where(EngagementEvent.employee_id == target.id)
        .order_by(EngagementEvent.occurred_at.desc())
        .limit(12)
    )
    events = events_result.scalars().all()
    score = employee_engagement_score(target)
    trend_value = (snapshots[0].trend if snapshots else None) or 0
    trend_label = "stable" if trend_value == 0 else "hausse" if trend_value > 0 else "baisse"
    risk_band = snapshots[0].risk_band if snapshots and snapshots[0].risk_band else ("high" if score < 55 else "medium" if score < 70 else "low")

    return EmployeeEngagementResponse(
        employee_id=target.id,
        current_score=score,
        trend_label=trend_label,
        risk_band=risk_band,
        snapshots=[
            EngagementSnapshotItem(
                id=item.id,
                score=item.score,
                source=item.source,
                pulse_label=item.pulse_label,
                comment=item.comment,
                trend=item.trend,
                risk_band=item.risk_band,
                source_signals=item.source_signals,
                captured_at=item.captured_at,
            )
            for item in snapshots[:12]
        ],
        events=[
            EngagementEventItem(
                id=item.id,
                event_type=item.event_type,
                label=item.label,
                intensity=item.intensity,
                source=item.source,
                payload=item.payload,
                occurred_at=item.occurred_at,
            )
            for item in events
        ],
    )


@router.get("/employees/{employee_id}/performance", response_model=EmployeePerformanceResponse, dependencies=[Depends(read_roles)])
async def get_employee_performance(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, target = await _resolve_target_employee(employee_id, current_user, db)
    reviews_result = await db.execute(
        select(PerformanceReview)
        .options(selectinload(PerformanceReview.reviewer))
        .where(PerformanceReview.employee_id == target.id)
        .order_by(PerformanceReview.created_at.desc())
    )
    reviews = reviews_result.scalars().all()
    objectives_result = await db.execute(
        select(PerformanceObjective)
        .options(selectinload(PerformanceObjective.owner))
        .where(PerformanceObjective.employee_id == target.id)
        .order_by(PerformanceObjective.target_date.asc(), PerformanceObjective.created_at.desc())
    )
    objectives = objectives_result.scalars().all()

    review_items = [
        PerformanceReviewItem(
            id=item.id,
            review_type=item.review_type,
            period_label=item.period_label,
            score=item.score,
            summary=item.summary,
            strengths=item.strengths or [],
            improvement_areas=item.improvement_areas or [],
            reviewer_name=f"{item.reviewer.first_name} {item.reviewer.last_name}".strip() if item.reviewer else None,
            created_at=item.created_at,
        )
        for item in reviews
    ]
    objective_items = [
        PerformanceObjectiveItem(
            id=item.id,
            title=item.title,
            description=item.description,
            status=item.status,
            progress_pct=item.progress_pct,
            target_date=item.target_date,
            owner_name=f"{item.owner.first_name} {item.owner.last_name}".strip() if item.owner else None,
        )
        for item in objectives
    ]

    return EmployeePerformanceResponse(
        employee_id=target.id,
        current_score=employee_performance_score(target),
        latest_review=review_items[0] if review_items else None,
        reviews=review_items[:8],
        objectives=objective_items,
    )


@router.post("/employees/{employee_id}/objectives", response_model=PerformanceObjectiveItem, dependencies=[Depends(write_roles)])
async def create_performance_objective(
    employee_id: str,
    payload: ObjectiveCreatePayload,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_employee, target = await _resolve_target_employee(employee_id, current_user, db)
    objective = PerformanceObjective(
        employee_id=target.id,
        owner_id=current_employee.id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        progress_pct=payload.progress_pct,
        target_date=payload.target_date,
    )
    db.add(objective)
    await db.commit()
    await db.refresh(objective)
    return PerformanceObjectiveItem(
        id=objective.id,
        title=objective.title,
        description=objective.description,
        status=objective.status,
        progress_pct=objective.progress_pct,
        target_date=objective.target_date,
        owner_name=f"{current_employee.first_name} {current_employee.last_name}".strip(),
    )
