from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models.domain import Employee
from app.services.keycloak_admin_service import keycloak_admin_service
from app.services.role_mapping_service import infer_access_role_for_employee

logger = logging.getLogger(__name__)


def username_from_email(email: str) -> str:
    return email.split("@", 1)[0].strip().lower()


async def sync_employee_identity(employee_id: str, db: AsyncSession) -> Employee:
    result = await db.execute(
        select(Employee)
        .options(selectinload(Employee.department), selectinload(Employee.job))
        .filter(Employee.id == employee_id)
    )
    employee = result.scalar_one()
    role = infer_access_role_for_employee(employee)
    keycloak_user = await keycloak_admin_service.create_or_update_user(
        username=username_from_email(employee.email),
        email=employee.email,
        first_name=employee.first_name,
        last_name=employee.last_name,
        role=role,
        enabled=employee.status != "inactif",
    )
    if employee.user_id != keycloak_user["id"]:
        employee.user_id = keycloak_user["id"]
        await db.commit()
        await db.refresh(employee)
    return employee
