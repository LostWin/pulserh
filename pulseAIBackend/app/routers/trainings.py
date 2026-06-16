from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_any_role
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Employee, EmployeeSkill, ProjectAssignment, Skill, TrainingCourse, TrainingEnrollment
from app.schemas.auth import CurrentUser
from app.schemas.talent import (
    AssignTrainingPayload,
    CompleteTrainingPayload,
    TrainingCatalogItem,
    TrainingEnrollmentItem,
    TrainingRecommendationItem,
)
from app.services.current_employee_service import get_or_create_current_employee
from app.services.training_recommendation_service import recommend_trainings_for_employee

router = APIRouter(tags=["Trainings"])

read_roles = require_any_role("collaborator", "manager", "hr", "director", "admin")
assign_roles = require_any_role("manager", "hr", "admin")


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
            selectinload(Employee.skills).selectinload(EmployeeSkill.skill),
            selectinload(Employee.job),
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
            selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
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


def _serialize_training_course(training: TrainingCourse) -> TrainingCatalogItem:
    return TrainingCatalogItem(
        id=training.id,
        title=training.title,
        provider=training.provider,
        duration_hours=training.duration_hours,
        level=training.level,
        format=training.format,
        description=training.description,
        target_skill_id=training.target_skill_id,
        target_skill_name=training.target_skill.name if training.target_skill else None,
        required_for_job_family=training.required_for_job_family,
        difficulty=training.difficulty,
        delivery_mode=training.delivery_mode or training.format,
        mandatory_for_roles=training.mandatory_for_roles or [],
    )


def _serialize_enrollment(item: TrainingEnrollment) -> TrainingEnrollmentItem:
    return TrainingEnrollmentItem(
        id=item.id,
        employee_id=item.employee_id,
        training_id=item.training_id,
        title=item.training.title if item.training else "Formation",
        provider=item.training.provider if item.training else None,
        status=item.status,
        mandatory=item.mandatory,
        assigned_at=item.assigned_at,
        due_date=item.due_date,
        completed_at=item.completed_at,
        score=item.score,
        assigned_by=item.assigned_by,
        recommendation_reason=item.recommendation_reason,
    )


@router.get("/trainings/catalog", response_model=list[TrainingCatalogItem], dependencies=[Depends(read_roles)])
async def get_trainings_catalog(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TrainingCourse).options(selectinload(TrainingCourse.target_skill)).order_by(TrainingCourse.title)
    )
    return [_serialize_training_course(item) for item in result.scalars().all()]


@router.get("/employees/{employee_id}/trainings", response_model=list[TrainingEnrollmentItem], dependencies=[Depends(read_roles)])
async def get_employee_trainings(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, target = await _resolve_target_employee(employee_id, current_user, db)
    return [_serialize_enrollment(item) for item in target.training_enrollments]


@router.post("/employees/{employee_id}/trainings/assign", response_model=TrainingEnrollmentItem, dependencies=[Depends(assign_roles)])
async def assign_training(
    employee_id: str,
    payload: AssignTrainingPayload,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_employee, target = await _resolve_target_employee(employee_id, current_user, db)
    training = await db.get(TrainingCourse, payload.training_id)
    if not training:
        raise HTTPException(status_code=404, detail="Formation introuvable.")

    existing_result = await db.execute(
        select(TrainingEnrollment)
        .options(selectinload(TrainingEnrollment.training))
        .where(TrainingEnrollment.employee_id == target.id, TrainingEnrollment.training_id == training.id)
    )
    enrollment = existing_result.scalar_one_or_none()
    if enrollment:
        enrollment.status = "assigned"
        enrollment.due_date = payload.due_date or enrollment.due_date
        enrollment.mandatory = payload.mandatory
        enrollment.assigned_by = f"{current_employee.first_name} {current_employee.last_name}".strip()
        enrollment.recommendation_reason = payload.recommendation_reason
    else:
        enrollment = TrainingEnrollment(
            employee_id=target.id,
            training_id=training.id,
            status="assigned",
            assigned_at=datetime.now(timezone.utc),
            due_date=payload.due_date,
            mandatory=payload.mandatory,
            assigned_by=f"{current_employee.first_name} {current_employee.last_name}".strip(),
            recommendation_reason=payload.recommendation_reason,
        )
        db.add(enrollment)
    await db.commit()
    refreshed = await db.execute(
        select(TrainingEnrollment)
        .options(selectinload(TrainingEnrollment.training))
        .where(TrainingEnrollment.id == enrollment.id)
    )
    enrollment = refreshed.scalar_one()
    return _serialize_enrollment(enrollment)


@router.post("/trainings/{training_id}/complete", response_model=TrainingEnrollmentItem, dependencies=[Depends(read_roles)])
async def complete_training(
    training_id: str,
    payload: CompleteTrainingPayload,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_employee, target = await _resolve_target_employee(payload.employee_id, current_user, db)
    if "collaborator" in current_user.roles and target.id != current_employee.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez valider que vos propres formations.")

    result = await db.execute(
        select(TrainingEnrollment)
        .options(selectinload(TrainingEnrollment.training))
        .where(TrainingEnrollment.employee_id == target.id, TrainingEnrollment.training_id == training_id)
    )
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Affectation de formation introuvable.")

    enrollment.status = "completed"
    enrollment.completed_at = datetime.now(timezone.utc)
    if payload.score is not None:
        enrollment.score = payload.score
    await db.commit()
    refreshed = await db.execute(
        select(TrainingEnrollment)
        .options(selectinload(TrainingEnrollment.training))
        .where(TrainingEnrollment.id == enrollment.id)
    )
    enrollment = refreshed.scalar_one()
    return _serialize_enrollment(enrollment)


@router.get("/trainings/recommendations/{employee_id}", response_model=list[TrainingRecommendationItem], dependencies=[Depends(read_roles)])
async def get_training_recommendations(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, target = await _resolve_target_employee(employee_id, current_user, db)
    trainings_result = await db.execute(
        select(TrainingCourse).options(selectinload(TrainingCourse.target_skill)).order_by(TrainingCourse.title)
    )
    trainings = trainings_result.scalars().all()
    skills_result = await db.execute(select(Skill))
    skills_by_id = {skill.id: skill for skill in skills_result.scalars().all()}
    return recommend_trainings_for_employee(target, trainings, skills_by_id)
