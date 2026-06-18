from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_any_role, require_hr
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Employee, EmployeeSkill, Skill
from app.schemas.auth import CurrentUser
from app.schemas.talent import (
    EmployeeSkillCreate,
    EmployeeSkillItem,
    EmployeeSkillUpdate,
    SkillCatalogItem,
    ValidateSkillPayload,
)
from app.services.current_employee_service import get_or_create_current_employee
from app.services.audit_service import log_audit

router = APIRouter(tags=["Skills"])

read_roles = require_any_role("collaborator", "manager", "hr", "director", "admin")
validate_roles = require_any_role("manager", "hr", "admin")


async def _resolve_target_employee(
    employee_id: str,
    current_user: CurrentUser,
    db: AsyncSession,
) -> tuple[Employee, Employee]:
    current_employee = await get_or_create_current_employee(current_user, db)
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.skills).selectinload(EmployeeSkill.skill),
            selectinload(Employee.manager),
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


def _serialize_employee_skill(item: EmployeeSkill) -> EmployeeSkillItem:
    return EmployeeSkillItem(
        id=item.id,
        employee_id=item.employee_id,
        skill_id=item.skill_id,
        skill_name=item.skill.name if item.skill else "Compétence",
        category=item.skill.category if item.skill else None,
        proficiency_level=item.proficiency_level,
        years_experience=item.years_experience,
        is_primary=item.is_primary,
        source=item.source,
        validated_by=item.validated_by,
        validated_at=item.validated_at,
        last_assessed_at=item.last_assessed_at,
        last_used_at=item.last_used_at,
        confidence_score=item.confidence_score,
    )


@router.get("/skills/catalog", response_model=list[SkillCatalogItem], dependencies=[Depends(read_roles)])
async def get_skills_catalog(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill).where(Skill.is_active.is_(True)).order_by(Skill.category, Skill.name))
    return result.scalars().all()


@router.get("/employees/{employee_id}/skills", response_model=list[EmployeeSkillItem], dependencies=[Depends(read_roles)])
async def get_employee_skills(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, target = await _resolve_target_employee(employee_id, current_user, db)
    return [_serialize_employee_skill(item) for item in sorted(target.skills, key=lambda row: (not row.is_primary, row.skill.name if row.skill else ""))]


@router.post("/employees/{employee_id}/skills", response_model=EmployeeSkillItem, dependencies=[Depends(require_hr)])
async def add_employee_skill(
    employee_id: str,
    payload: EmployeeSkillCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, target = await _resolve_target_employee(employee_id, current_user, db)
    skill = await db.get(Skill, payload.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Compétence introuvable.")

    existing = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill))
        .where(EmployeeSkill.employee_id == target.id, EmployeeSkill.skill_id == payload.skill_id)
    )
    employee_skill = existing.scalar_one_or_none()
    if employee_skill:
        raise HTTPException(status_code=409, detail="Cette compétence est déjà associée au collaborateur.")

    if payload.is_primary:
        await db.execute(
            select(EmployeeSkill).where(EmployeeSkill.employee_id == target.id)
        )
        for row in target.skills:
            row.is_primary = False

    employee_skill = EmployeeSkill(
        employee_id=target.id,
        skill_id=payload.skill_id,
        proficiency_level=payload.proficiency_level,
        years_experience=payload.years_experience,
        is_primary=payload.is_primary,
        source=payload.source or "hr_manual",
        last_assessed_at=payload.last_assessed_at,
        last_used_at=payload.last_used_at,
        confidence_score=payload.confidence_score,
    )
    db.add(employee_skill)
    await db.commit()
    refreshed = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill))
        .where(EmployeeSkill.id == employee_skill.id)
    )
    employee_skill = refreshed.scalar_one()
    await log_audit(
        db, current_user.email,
        f"Ajout compétence '{skill.name}' à employee {target.id}",
        "hr_action",
        details={"employee_id": target.id, "skill_id": payload.skill_id, "skill_name": skill.name, "proficiency_level": payload.proficiency_level},
    )
    return _serialize_employee_skill(employee_skill)("/employees/{employee_id}/skills/{skill_id}", response_model=EmployeeSkillItem, dependencies=[Depends(require_hr)])
async def update_employee_skill(
    employee_id: str,
    skill_id: str,
    payload: EmployeeSkillUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, target = await _resolve_target_employee(employee_id, current_user, db)
    result = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill))
        .where(EmployeeSkill.employee_id == target.id, EmployeeSkill.skill_id == skill_id)
    )
    employee_skill = result.scalar_one_or_none()
    if not employee_skill:
        raise HTTPException(status_code=404, detail="Compétence collaborateur introuvable.")

    if payload.is_primary:
        for row in target.skills:
            if row.id != employee_skill.id:
                row.is_primary = False

    for field in ["proficiency_level", "years_experience", "is_primary", "source", "last_assessed_at", "last_used_at", "confidence_score"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(employee_skill, field, value)

    await db.commit()
    refreshed = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill))
        .where(EmployeeSkill.id == employee_skill.id)
    )
    employee_skill = refreshed.scalar_one()
    await log_audit(
        db, current_user.email,
        f"Mise à jour compétence {skill_id} pour employee {employee_id}",
        "hr_action",
        details={"employee_id": employee_id, "skill_id": skill_id, "proficiency_level": payload.proficiency_level},
    )
    return _serialize_employee_skill(employee_skill)


@router.post("/employees/{employee_id}/skills/{skill_id}/validate", response_model=EmployeeSkillItem, dependencies=[Depends(validate_roles)])
async def validate_employee_skill(
    employee_id: str,
    skill_id: str,
    payload: ValidateSkillPayload,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_employee, target = await _resolve_target_employee(employee_id, current_user, db)
    result = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill))
        .where(EmployeeSkill.employee_id == target.id, EmployeeSkill.skill_id == skill_id)
    )
    employee_skill = result.scalar_one_or_none()
    if not employee_skill:
        raise HTTPException(status_code=404, detail="Compétence collaborateur introuvable.")

    validator_name = payload.validated_by or f"{current_employee.first_name} {current_employee.last_name}".strip()
    employee_skill.validated_by = validator_name
    employee_skill.validated_at = datetime.now(timezone.utc)
    if employee_skill.source is None:
        employee_skill.source = "validated_manager"
    await db.commit()
    refreshed = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill))
        .where(EmployeeSkill.id == employee_skill.id)
    )
    employee_skill = refreshed.scalar_one()
    await log_audit(
        db, current_user.email,
        f"Validation compétence {skill_id} pour employee {employee_id} par {validator_name}",
        "hr_action",
        details={"employee_id": employee_id, "skill_id": skill_id, "validated_by": validator_name},
    )
    return _serialize_employee_skill(employee_skill)
