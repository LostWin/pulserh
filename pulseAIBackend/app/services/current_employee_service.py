from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Employee
from app.schemas.auth import CurrentUser


def _default_first_name(current_user: CurrentUser) -> str:
    if current_user.first_name:
        return current_user.first_name
    if current_user.username:
        return current_user.username.split(".")[0].replace("-", " ").title()
    if current_user.full_name:
        return current_user.full_name.split(" ")[0]
    return "Utilisateur"


def _default_last_name(current_user: CurrentUser) -> str:
    if current_user.last_name:
        return current_user.last_name
    if current_user.username and "." in current_user.username:
        return current_user.username.split(".", 1)[1].replace("-", " ").title()
    if current_user.full_name and " " in current_user.full_name.strip():
        return current_user.full_name.strip().split(" ", 1)[1]
    return "Pulse"


async def get_or_create_current_employee(
    current_user: CurrentUser,
    db: AsyncSession,
    *,
    extra_options: list[Any] | None = None,
) -> Employee:
    options = list(extra_options or [])
    query = select(Employee).options(*options)

    filters = [Employee.user_id == current_user.id]
    if current_user.email:
        filters.append(Employee.email == current_user.email)
    if current_user.first_name and current_user.last_name:
        filters.append(
            (func.lower(Employee.first_name) == current_user.first_name.lower())
            & (func.lower(Employee.last_name) == current_user.last_name.lower())
        )

    result = await db.execute(query.filter(or_(*filters)))
    employee = result.scalar_one_or_none()
    if employee:
        changed = False
        if current_user.id and employee.user_id != current_user.id:
            employee.user_id = current_user.id
            changed = True
        if current_user.email and employee.email != current_user.email:
            employee.email = current_user.email
            changed = True
        if changed:
            await db.commit()
            await db.refresh(employee)
        return employee

    employee = Employee(
        user_id=current_user.id,
        first_name=_default_first_name(current_user),
        last_name=_default_last_name(current_user),
        email=current_user.email or f"{current_user.id}@pulse.local",
        hire_date=date.today(),
        status="actif",
    )
    db.add(employee)
    await db.commit()

    refresh_result = await db.execute(
        select(Employee).options(*options).filter(Employee.id == employee.id)
    )
    return refresh_result.scalar_one()
