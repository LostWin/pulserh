from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_collaborator
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Employee, Leave
from app.schemas.auth import CurrentUser
from app.schemas.leave import (
    LeaveActivityItem,
    LeaveAISuggestion,
    LeaveBalanceItem,
    LeaveCalendarEvent,
    LeaveOverviewResponse,
    LeaveRequestCreate,
    LeaveRequestItem,
)
from app.services.current_employee_service import get_or_create_current_employee
from app.services.field_access_service import apply_field_access, get_primary_role
from app.services.audit_service import log_audit

router = APIRouter(prefix="/leaves", tags=["Leaves"])


async def _get_current_employee(current_user: CurrentUser, db: AsyncSession) -> Employee:
    return await get_or_create_current_employee(
        current_user,
        db,
        extra_options=[selectinload(Employee.leaves)],
    )


def _days_inclusive(start_date: date, end_date: date) -> int:
    return max(0, (end_date - start_date).days + 1)


async def _serialize_leave_request(
    db: AsyncSession,
    *,
    leave: Leave,
    current_user: CurrentUser,
) -> LeaveRequestItem:
    payload = {
        "id": leave.id,
        "leave_type": leave.leave_type,
        "start_date": leave.start_date.isoformat(),
        "end_date": leave.end_date.isoformat(),
        "status": leave.status,
        "reason": leave.reason,
    }
    filtered, field_visibility = await apply_field_access(
        db,
        resource="leave",
        scope="request",
        payload=payload,
        role=get_primary_role(current_user.roles),
        context={"is_self": True},
    )
    filtered.pop("field_visibility", None)
    filtered.pop("_field_visibility", None)
    return LeaveRequestItem(**filtered, field_visibility=field_visibility)


async def _serialize_leave_suggestion(
    db: AsyncSession,
    *,
    suggestion: LeaveAISuggestion,
    current_user: CurrentUser,
) -> LeaveAISuggestion:
    payload = suggestion.model_dump()
    filtered, field_visibility = await apply_field_access(
        db,
        resource="leave",
        scope="suggestion",
        payload=payload,
        role=get_primary_role(current_user.roles),
        context={"is_self": True},
    )
    filtered.pop("field_visibility", None)
    filtered.pop("_field_visibility", None)
    return LeaveAISuggestion(**filtered, field_visibility=field_visibility)


@router.get("/me", response_model=LeaveOverviewResponse, dependencies=[Depends(require_collaborator)])
async def get_my_leaves(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    employee = await _get_current_employee(current_user, db)
    today = date.today()

    approved_leaves = [leave for leave in employee.leaves if leave.status == "Approuvé"]
    sick_leaves = [
        leave for leave in employee.leaves
        if "maladie" in (leave.leave_type or "").lower() and leave.start_date.year == today.year
    ]

    paid_used = sum(
        _days_inclusive(leave.start_date, leave.end_date)
        for leave in approved_leaves
        if "pay" in (leave.leave_type or "").lower() or "cong" in (leave.leave_type or "").lower()
    )
    paid_total = 30
    paid_remaining = max(0, paid_total - paid_used)
    rtt_total = 10
    rtt_used = sum(
        _days_inclusive(leave.start_date, leave.end_date)
        for leave in approved_leaves
        if "rtt" in (leave.leave_type or "").lower()
    )
    rtt_remaining = max(0, rtt_total - rtt_used)
    sick_ytd = sum(_days_inclusive(leave.start_date, leave.end_date) for leave in sick_leaves)

    balances = [
        LeaveBalanceItem(
            id="cp",
            label="PAID LEAVE BALANCE",
            value=float(paid_remaining),
            unit="days",
            tag="✓ Stable" if paid_remaining >= 10 else "⚠ Low",
            tag_color="text-emerald-600 bg-emerald-50" if paid_remaining >= 10 else "text-amber-600 bg-amber-50",
        ),
        LeaveBalanceItem(
            id="rtt",
            label="RTT BALANCE",
            value=float(rtt_remaining),
            unit="days",
            tag="⏰ Expires 31/12",
            tag_color="text-amber-600 bg-amber-50",
        ),
        LeaveBalanceItem(
            id="sick",
            label="SICK LEAVE (YTD)",
            value=float(sick_ytd),
            unit="days",
            tag="+ New Entry" if sick_ytd > 0 else "No use",
            tag_color="text-red-500 bg-red-50" if sick_ytd > 0 else "text-brand-secondary bg-brand-light",
        ),
    ]

    sorted_leaves = sorted(employee.leaves, key=lambda item: item.start_date, reverse=True)
    activity: list[LeaveActivityItem] = []
    color_map = {
        "Approuvé": "bg-emerald-500",
        "En attente": "bg-amber-400",
        "Rejeté": "bg-red-400",
    }
    for index, leave in enumerate(sorted_leaves[:5], start=1):
        status_label = leave.status or "En attente"
        date_label = leave.start_date.strftime("%d/%m/%Y")
        activity.append(
            LeaveActivityItem(
                id=str(index),
                title=f"{leave.leave_type} {status_label.lower()}",
                sub=f"Du {date_label} au {leave.end_date.strftime('%d/%m/%Y')}",
                color=color_map.get(status_label, "bg-brand-secondary"),
            )
        )

    calendar_events = [
        LeaveCalendarEvent(
            date=leave.start_date.isoformat(),
            label=f"{leave.status}\n{leave.leave_type}",
            color="#1F524B" if leave.status == "Approuvé" else "#DF4931",
            text="white",
        )
        for leave in sorted_leaves[:12]
    ]

    requests = [await _serialize_leave_request(db, leave=leave, current_user=current_user) for leave in sorted_leaves[:10]]

    ai_suggestion = LeaveAISuggestion(
        message=f"Vous avez {paid_remaining} jours de congés restants. Planifier un congé à l’avance aide à fluidifier la charge de l’équipe.",
        primary_action="Planifier mes congés",
        secondary_action="Me rappeler plus tard",
    )

    return LeaveOverviewResponse(
        balances=balances,
        calendar_events=calendar_events,
        activity=activity,
        requests=requests,
        ai_suggestion=await _serialize_leave_suggestion(db, suggestion=ai_suggestion, current_user=current_user),
    )


@router.post("/requests", response_model=LeaveRequestItem, dependencies=[Depends(require_collaborator)])
async def create_leave_request(
    payload: LeaveRequestCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    employee = await _get_current_employee(current_user, db)
    start_date = datetime.fromisoformat(payload.start_date).date()
    end_date = datetime.fromisoformat(payload.end_date).date()
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="La date de fin doit être postérieure à la date de début.")

    leave = Leave(
        employee_id=employee.id,
        leave_type=payload.leave_type,
        start_date=start_date,
        end_date=end_date,
        status="En attente",
        reason=payload.reason,
    )
    db.add(leave)
    await db.commit()
    await db.refresh(leave)

    await log_audit(
        db, current_user.email,
        f"Demande congé: {payload.leave_type} du {payload.start_date} au {payload.end_date}",
        "hr_action",
        details={"leave_id": leave.id, "employee_id": employee.id, "leave_type": payload.leave_type, "start": payload.start_date, "end": payload.end_date},
    )

    return await _serialize_leave_request(db, leave=leave, current_user=current_user)
