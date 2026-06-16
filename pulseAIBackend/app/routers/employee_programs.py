from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_, and_, String, cast, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_any_role, require_collaborator
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import CareerPath, Department, Employee, EmployeeBenefit, Job, MobilityRequest, TrainingEnrollment, Contract
from app.schemas.auth import CurrentUser
from app.schemas.employee_programs import (
    BenefitEnrollmentResponse,
    EmployeeCareerOverviewResponse,
    EmployeeProgramOverviewItem,
    EmployeeProgramOverviewResponse,
    EmployeeProgramsFiltersResponse,
    MobilityRequestCreate,
    MobilityRequestResponse,
    PromotionHistoryResponse,
    CareerPathResponse,
)
from app.services.current_employee_service import get_or_create_current_employee
from app.services.hr_analytics_service import benefits_status_for_employee
from app.services.field_access_service import (
    get_effective_policies,
    get_primary_role,
    resolve_visibility,
    apply_visibility,
    build_employee_access_context,
    apply_field_access,
)

router = APIRouter(prefix="/employees", tags=["Employee Programs"])


def _format_date(value) -> str | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y")
    return value.strftime("%d %b %Y")


def _get_tenure_label(hire_date: date | None) -> str | None:
    if not hire_date:
        return "N/A"
    today = date.today()
    days = (today - hire_date).days
    if days < 30:
        return f"{days} jour{'s' if days > 1 else ''}"
    elif days < 365:
        months = days // 30
        return f"{months} mois"
    else:
        years = days // 365
        return f"{years} an{'s' if years > 1 else ''}"


async def _get_target_employee(
    employee_id: str,
    current_user: CurrentUser,
    db: AsyncSession,
) -> Employee:
    target = (
        await db.execute(
            select(Employee).options(
                selectinload(Employee.benefit_enrollments).selectinload(EmployeeBenefit.benefit_plan),
                selectinload(Employee.career_paths).selectinload(CareerPath.target_job),
                selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_department),
                selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_job),
                selectinload(Employee.promotions),
            ).where(Employee.id == employee_id)
        )
    ).scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Employé introuvable.")

    if "hr" not in current_user.roles and "admin" not in current_user.roles and target.user_id != current_user.id and target.email != current_user.email:
        raise HTTPException(status_code=403, detail="Accès refusé.")
    return target


@router.get("/me/benefits", response_model=list[BenefitEnrollmentResponse], dependencies=[Depends(require_collaborator)])
async def get_my_benefits(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    employee = await get_or_create_current_employee(
        current_user,
        db,
        extra_options=[selectinload(Employee.benefit_enrollments).selectinload(EmployeeBenefit.benefit_plan)],
    )
    return [
        BenefitEnrollmentResponse(
            id=benefit.id,
            plan_name=benefit.benefit_plan.name if benefit.benefit_plan else "Plan",
            category=benefit.benefit_plan.category if benefit.benefit_plan else "general",
            provider=benefit.benefit_plan.provider if benefit.benefit_plan else None,
            status=benefit.status,
            tier_label=benefit.tier_label,
            effective_date_label=_format_date(benefit.effective_date),
            renewal_date_label=_format_date(benefit.renewal_date),
            employer_contribution=benefit.employer_contribution,
            coverage_summary=benefit.benefit_plan.coverage_summary if benefit.benefit_plan else benefit.notes,
        )
        for benefit in employee.benefit_enrollments
    ]


@router.get("/{employee_id}/career", response_model=EmployeeCareerOverviewResponse, dependencies=[Depends(require_any_role("collaborator", "hr", "admin"))])
async def get_employee_career_overview(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    employee = await _get_target_employee(employee_id, current_user, db)
    primary_role = get_primary_role(current_user.roles)
    context = build_employee_access_context(None, employee)
    
    career_paths = []
    for path in employee.career_paths:
        payload = {
            "id": path.id,
            "target_title": path.target_title,
            "readiness_level": path.readiness_level,
            "next_step": path.next_step,
            "mentor_name": path.mentor_name,
            "last_reviewed_at_label": _format_date(path.last_reviewed_at),
        }
        filtered, visibility = await apply_field_access(db, resource="career", scope="detail", payload=payload, role=primary_role, context=context)
        career_paths.append(CareerPathResponse(**filtered, _field_visibility=visibility))
        
    mobility_requests = []
    for request in sorted(employee.mobility_requests, key=lambda item: item.requested_at or datetime.min, reverse=True):
        payload = {
            "id": request.id,
            "request_type": request.request_type,
            "status": request.status,
            "target_department": request.target_department.name if request.target_department else None,
            "target_job_title": request.target_job.title if request.target_job else None,
            "rationale": request.rationale,
            "requested_at_label": _format_date(request.requested_at),
            "reviewed_at_label": _format_date(request.reviewed_at),
        }
        filtered, visibility = await apply_field_access(db, resource="career", scope="detail", payload=payload, role=primary_role, context=context)
        mobility_requests.append(MobilityRequestResponse(**filtered, _field_visibility=visibility))
        
    promotions = []
    for promotion in sorted(employee.promotions, key=lambda item: item.effective_date, reverse=True):
        payload = {
            "id": promotion.id,
            "previous_job_title": promotion.previous_job_title,
            "new_job_title": promotion.new_job_title,
            "effective_date_label": _format_date(promotion.effective_date) or "—",
            "notes": promotion.notes,
        }
        filtered, visibility = await apply_field_access(db, resource="career", scope="detail", payload=payload, role=primary_role, context=context)
        promotions.append(PromotionHistoryResponse(**filtered, _field_visibility=visibility))

    return EmployeeCareerOverviewResponse(
        career_paths=career_paths,
        mobility_requests=mobility_requests,
        promotions=promotions,
    )


@router.post("/me/mobility-request", response_model=MobilityRequestResponse, dependencies=[Depends(require_collaborator)])
async def create_my_mobility_request(
    payload: MobilityRequestCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    employee = await get_or_create_current_employee(current_user, db)
    target_department = None
    target_job = None

    if payload.target_department:
        target_department = (
            await db.execute(
                select(Department).where((Department.id == payload.target_department) | (Department.name == payload.target_department))
            )
        ).scalar_one_or_none()
    if payload.target_job_title:
        target_job = (
            await db.execute(select(Job).where((Job.id == payload.target_job_title) | (Job.title == payload.target_job_title)))
        ).scalar_one_or_none()

    request = MobilityRequest(
        employee_id=employee.id,
        target_department_id=target_department.id if target_department else None,
        target_job_id=target_job.id if target_job else None,
        request_type=payload.request_type,
        status="submitted",
        rationale=payload.rationale,
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return MobilityRequestResponse(
        id=request.id,
        request_type=request.request_type,
        status=request.status,
        target_department=target_department.name if target_department else None,
        target_job_title=target_job.title if target_job else None,
        rationale=request.rationale,
        requested_at_label=_format_date(request.requested_at),
        reviewed_at_label=_format_date(request.reviewed_at),
    )


@router.get("/programs/overview/filters", response_model=EmployeeProgramsFiltersResponse, dependencies=[Depends(require_any_role("hr", "admin"))])
async def get_employee_programs_filters(db: AsyncSession = Depends(get_db)):
    # Fetch distinct departments
    depts = (await db.execute(select(Department.name).distinct())).scalars().all()
    departments = ["all"] + sorted([d for d in depts if d])

    # Distinct readiness levels
    levels = (await db.execute(select(CareerPath.readiness_level).distinct())).scalars().all()
    readiness_levels = ["all"] + sorted([l for l in levels if l])

    # Distinct mobility statuses
    statuses = (await db.execute(select(MobilityRequest.status).distinct())).scalars().all()
    mobility_statuses = ["all", "open"] + sorted([s for s in statuses if s])

    # Benefits statuses (since they are computed dynamically from multiple tables, we'll keep the static list, or dynamically evaluate but static is cleaner here as they are hardcoded labels)
    benefits_statuses = ["all", "Active", "Premium", "Renouvellement requis", "À régulariser", "Vérification en cours"]

    return EmployeeProgramsFiltersResponse(
        departments=departments,
        readiness_levels=readiness_levels,
        benefits_statuses=benefits_statuses,
        mobility_statuses=list(dict.fromkeys(mobility_statuses)), # remove duplicates if "open" is also in statuses
    )


@router.get("/programs/overview", response_model=EmployeeProgramOverviewResponse, dependencies=[Depends(require_any_role("hr", "admin"))])
async def get_employee_programs_overview(
    q: str | None = Query(None, description="Search by name"),
    department: str | None = Query(None, description="Filter by department"),
    readiness_level: str | None = Query(None, description="Filter by readiness"),
    benefits_status: str | None = Query(None, description="Filter by benefits"),
    mobility_status: str | None = Query(None, description="Filter by mobility status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_employee = (await db.execute(select(Employee).where(Employee.user_id == current_user.id))).scalar_one_or_none()
    primary_role = get_primary_role(current_user.roles)

    policy_map = {
        item.field_key: item
        for item in await get_effective_policies(db, "employee", "list")
        if item.role == primary_role
    }

    base_stmt = select(Employee)

    if q:
        base_stmt = base_stmt.where(
            or_(
                Employee.first_name.ilike(f"%{q}%"),
                Employee.last_name.ilike(f"%{q}%"),
            )
        )
    if department:
        base_stmt = base_stmt.where(Employee.department.has(Department.name == department))

    filtered_stmt = base_stmt

    if readiness_level:
        filtered_stmt = filtered_stmt.where(Employee.career_paths.any(CareerPath.readiness_level == readiness_level))

    if mobility_status:
        if mobility_status == "open":
            filtered_stmt = filtered_stmt.where(Employee.mobility_requests.any(MobilityRequest.status.in_(["draft", "submitted", "reviewed"])))
        else:
            filtered_stmt = filtered_stmt.where(Employee.mobility_requests.any(MobilityRequest.status == mobility_status))

    if benefits_status:
        if benefits_status == "Premium":
            filtered_stmt = filtered_stmt.where(Employee.benefit_enrollments.any(and_(EmployeeBenefit.status.in_(["active", "eligible", "enrolled"]), EmployeeBenefit.tier_label.ilike("premium%"))))
        elif benefits_status == "Active":
            filtered_stmt = filtered_stmt.where(Employee.benefit_enrollments.any(EmployeeBenefit.status.in_(["active", "eligible", "enrolled"])))
        elif benefits_status == "Renouvellement requis":
            filtered_stmt = filtered_stmt.where(Employee.benefit_enrollments.any(and_(EmployeeBenefit.status.in_(["active", "eligible", "enrolled"]), EmployeeBenefit.renewal_date < date.today())))
        elif benefits_status == "Vérification en cours":
            filtered_stmt = filtered_stmt.where(Employee.training_enrollments.any(and_(TrainingEnrollment.mandatory == True, TrainingEnrollment.status != "completed")))
        elif benefits_status == "À régulariser":
            filtered_stmt = filtered_stmt.where(or_(Employee.status != "actif", ~Employee.contracts.any(Contract.is_active == True)))

    # Compute totals
    total_items = await db.scalar(select(func.count(Employee.id)).select_from(filtered_stmt.subquery()))
    
    ready_now_count = await db.scalar(select(func.count(Employee.id)).select_from(base_stmt.where(Employee.career_paths.any(CareerPath.readiness_level == "ready_now")).subquery()))
    mobility_open_count = await db.scalar(select(func.count(Employee.id)).select_from(base_stmt.where(Employee.mobility_requests.any(MobilityRequest.status.in_(["draft", "submitted", "reviewed"]))).subquery()))
    active_benefits_count = await db.scalar(select(func.count(Employee.id)).select_from(base_stmt.where(Employee.benefit_enrollments.any(EmployeeBenefit.status.in_(["active", "eligible", "enrolled"]))).subquery()))

    # Fetch paginated results
    paginated_stmt = filtered_stmt.options(
        selectinload(Employee.department),
        selectinload(Employee.job),
        selectinload(Employee.contracts),
        selectinload(Employee.benefit_enrollments).selectinload(EmployeeBenefit.benefit_plan),
        selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
        selectinload(Employee.career_paths).selectinload(CareerPath.target_job),
        selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_department),
        selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_job),
        selectinload(Employee.promotions),
        selectinload(Employee.manager),
    ).offset((page - 1) * page_size).limit(page_size)

    employees = (await db.execute(paginated_stmt)).scalars().all()

    items: list[EmployeeProgramOverviewItem] = []

    for employee in employees:
        primary_benefit = next(
            (benefit for benefit in employee.benefit_enrollments if benefit.status in {"active", "eligible", "enrolled"} and benefit.benefit_plan),
            employee.benefit_enrollments[0] if employee.benefit_enrollments else None,
        )
        # Re-evaluate the status for display
        emp_benefits_status = benefits_status_for_employee(employee)

        career_focus = next(
            (
                path for path in sorted(
                    employee.career_paths,
                    key=lambda item: item.last_reviewed_at or datetime.min,
                    reverse=True,
                )
            ),
            None,
        )

        mobility = next(
            (
                request for request in sorted(
                    employee.mobility_requests,
                    key=lambda item: item.requested_at or datetime.min,
                    reverse=True,
                )
            ),
            None,
        )

        promotion = next(
            (
                promotion for promotion in sorted(
                    employee.promotions,
                    key=lambda item: item.effective_date,
                    reverse=True,
                )
            ),
            None,
        )

        mobility_target = None
        if mobility:
            parts = [
                mobility.target_department.name if mobility.target_department else None,
                mobility.target_job.title if mobility.target_job else None,
            ]
            mobility_target = " · ".join([part for part in parts if part]) or None

        next_review_label = "À planifier"
        if career_focus and career_focus.last_reviewed_at:
            next_date = career_focus.last_reviewed_at + timedelta(days=365)
            next_review_label = _format_date(next_date)

        raw_payload = {
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "department": employee.department.name if employee.department else None,
            "job_title": employee.job.title if employee.job else None,
            "benefits_status": emp_benefits_status,
            "primary_benefit_label": primary_benefit.benefit_plan.name if primary_benefit and primary_benefit.benefit_plan else None,
            "career_focus_title": career_focus.target_title if career_focus else None,
            "readiness_level": career_focus.readiness_level if career_focus else None,
            "mobility_status": mobility.status if mobility else None,
            "mobility_target": mobility_target,
            "promotion_last_title": promotion.new_job_title if promotion else None,
            "promotion_effective_date_label": _format_date(promotion.effective_date) if promotion else None,
            "manager_name": f"{employee.manager.first_name} {employee.manager.last_name}" if employee.manager else None,
            "tenure_label": _get_tenure_label(employee.hire_date),
            "next_career_review_label": next_review_label,
        }

        context = build_employee_access_context(current_employee, employee)
        filtered = dict(raw_payload)
        field_visibility = {}

        for field_key, value in raw_payload.items():
            policy = policy_map.get(field_key)
            if policy is None:
                field_visibility[field_key] = "visible"
                continue
            visibility = resolve_visibility(policy, context)
            filtered[field_key] = apply_visibility(value, visibility, policy.mask_type)
            field_visibility[field_key] = visibility

        filtered["_field_visibility"] = field_visibility
        
        items.append(EmployeeProgramOverviewItem(**filtered))

    items.sort(key=lambda item: (item.mobility_status not in {"submitted", "reviewed"}, item.readiness_level != "ready_now", item.employee_name))

    return EmployeeProgramOverviewResponse(
        items=items,
        total=total_items or 0,
        page=page,
        page_size=page_size,
        active_benefits_count=active_benefits_count or 0,
        mobility_open_count=mobility_open_count or 0,
        ready_now_count=ready_now_count or 0,
    )
