from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_any_role
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Employee, Project, ProjectAssignment, Skill
from app.schemas.auth import CurrentUser
from app.schemas.talent import EmployeeProjectAssignmentItem, ProjectItem
from app.services.current_employee_service import get_or_create_current_employee

router = APIRouter(tags=["Projects"])

read_roles = require_any_role("collaborator", "manager", "hr", "director", "admin")


def _skill_name_index(skills: list[Skill]) -> dict[str, str]:
    return {skill.id: skill.name for skill in skills}


def _serialize_project(project: Project, names_by_id: dict[str, str]) -> ProjectItem:
    return ProjectItem(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        deadline=project.deadline,
        status=project.status,
        priority=project.priority,
        business_domain=project.business_domain,
        required_skill_ids=project.required_skill_ids or [],
        required_skill_names=[names_by_id[skill_id] for skill_id in (project.required_skill_ids or []) if skill_id in names_by_id],
        manager_id=project.manager_id,
        manager_name=f"{project.manager.first_name} {project.manager.last_name}".strip() if project.manager else None,
    )


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
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
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


@router.get("/projects", response_model=list[ProjectItem], dependencies=[Depends(read_roles)])
async def list_projects(db: AsyncSession = Depends(get_db)):
    skills = (await db.execute(select(Skill))).scalars().all()
    names_by_id = _skill_name_index(skills)
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.manager))
        .order_by(Project.status, Project.deadline, Project.name)
    )
    return [_serialize_project(project, names_by_id) for project in result.scalars().all()]


@router.get("/projects/{project_id}", response_model=ProjectItem, dependencies=[Depends(read_roles)])
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    skills = (await db.execute(select(Skill))).scalars().all()
    names_by_id = _skill_name_index(skills)
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.manager))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    return _serialize_project(project, names_by_id)


@router.get("/employees/{employee_id}/projects", response_model=list[EmployeeProjectAssignmentItem], dependencies=[Depends(read_roles)])
async def get_employee_projects(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, target = await _resolve_target_employee(employee_id, current_user, db)
    skills = (await db.execute(select(Skill))).scalars().all()
    names_by_id = _skill_name_index(skills)
    items: list[EmployeeProjectAssignmentItem] = []
    for assignment in target.project_assignments:
        if not assignment.project:
            continue
        items.append(
            EmployeeProjectAssignmentItem(
                id=assignment.id,
                project_id=assignment.project_id,
                project_name=assignment.project.name,
                status=assignment.project.status,
                priority=assignment.project.priority,
                business_domain=assignment.project.business_domain,
                role_on_project=assignment.role_on_project,
                allocation_pct=assignment.allocation_pct,
                start_date=assignment.start_date,
                end_date=assignment.end_date,
                is_active=assignment.is_active,
                required_skill_names=[names_by_id[skill_id] for skill_id in (assignment.project.required_skill_ids or []) if skill_id in names_by_id],
            )
        )
    return items


@router.get("/teams/{manager_id}/projects", response_model=list[ProjectItem], dependencies=[Depends(read_roles)])
async def get_team_projects(
    manager_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_employee = await get_or_create_current_employee(current_user, db)
    if "manager" in current_user.roles and current_employee.id != manager_id and not ({"hr", "director", "admin"} & set(current_user.roles)):
        raise HTTPException(status_code=403, detail="Vous ne pouvez consulter que les projets de votre équipe.")

    skills = (await db.execute(select(Skill))).scalars().all()
    names_by_id = _skill_name_index(skills)
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.manager))
        .join(Project.assignments)
        .join(ProjectAssignment.employee)
        .where(Employee.manager_id == manager_id)
        .distinct()
        .order_by(Project.deadline, Project.name)
    )
    return [_serialize_project(project, names_by_id) for project in result.scalars().all()]
