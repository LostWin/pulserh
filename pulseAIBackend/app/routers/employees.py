import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.domain import Contract, Department, Employee, Job, ProjectAssignment, TrainingEnrollment, UserPreference, EmployeeSkill, Task, EmployeeBenefit, CareerPath, MobilityRequest
from app.services.audit_service import log_audit_action
from app.services.current_employee_service import get_or_create_current_employee
from app.services.employee_identity_service import sync_employee_identity
from app.services.field_access_service import (
    apply_field_access,
    build_employee_access_context,
    get_primary_role,
)

from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse,
    ImportReport, ChangeRequest, EmployeeProfileSummaryResponse, EmployeeSkillBadge,
    EmployeeCompetencyItem, EmployeeAccomplishmentItem
)
from app.schemas.import_schemas import ImportHistoryResponse
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_hr, require_any_role, require_collaborator
from app.services.hr_analytics_service import benefits_status_for_employee, current_project_names, employee_engagement_score, employee_performance_score, employee_risk_payload
from app.services.risk_predictor import risk_predictor

router = APIRouter(prefix="/employees", tags=["Employees"])
logger = logging.getLogger(__name__)


async def _build_employee_payload(
    emp: Employee,
    *,
    contract_type: str | None,
    salary: float | None,
    leave_balance: str | None,
    db: AsyncSession,
) -> dict:
    prioritized_objective = next(
        (
            objective for objective in sorted(
                emp.performance_objectives,
                key=lambda item: (item.status != "in_progress", -(item.progress_pct or 0)),
            )
            if objective.status != "completed"
        ),
        None,
    )
    latest_mobility = next(
        (
            request for request in sorted(
                emp.mobility_requests,
                key=lambda item: item.requested_at or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
        ),
        None,
    )
    risk_payload = await risk_predictor.predict(emp, db)
    return {
        "id": emp.id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "department": emp.department.name if emp.department else None,
        "job_title": emp.job.title if emp.job else None,
        "status": emp.status,
        "contract_type": contract_type,
        "manager_id": emp.manager_id,
        "salary": salary,
        "phone": emp.phone,
        "hire_date": emp.hire_date.strftime("%d %B %Y") if emp.hire_date else None,
        "manager_name": f"{emp.manager.first_name} {emp.manager.last_name}" if emp.manager else "Aucun manager",
        "leave_balance": leave_balance,
        "engagement_score": employee_engagement_score(emp),
        "risk_level": (
            "high"
            if risk_payload["level"] == "red"
            else "medium"
            if risk_payload["level"] == "orange"
            else "low"
        ),
        "risk_score": round(risk_payload["score_pct"]),
        "trend_delta": max(-12, min(8, round((employee_engagement_score(emp) - 72) / 3))),
        "last_active_label": "Aujourd'hui" if current_project_names(emp) else "À relancer",
        "project_count": len(current_project_names(emp)),
        "performance_score": employee_performance_score(emp),
        "focus_objective_title": prioritized_objective.title if prioritized_objective else None,
        "focus_objective_progress_pct": prioritized_objective.progress_pct if prioritized_objective else None,
        "benefits_status": benefits_status_for_employee(emp),
        "mobility_status": latest_mobility.status if latest_mobility else "none",
    }


async def _serialize_employee_response(
    *,
    db: AsyncSession,
    current_user: CurrentUser,
    current_employee: Employee | None,
    target_employee: Employee,
    scope: str,
    contract_type: str | None,
    salary: float | None,
    leave_balance: str | None,
) -> EmployeeResponse:
    payload = await _build_employee_payload(
        target_employee,
        contract_type=contract_type,
        salary=salary,
        leave_balance=leave_balance,
        db=db,
    )
    filtered_payload, field_visibility = await apply_field_access(
        db,
        resource="employee",
        scope=scope,
        payload=payload,
        role=get_primary_role(current_user.roles),
        context=build_employee_access_context(current_employee, target_employee),
    )
    return EmployeeResponse(**filtered_payload, field_visibility=field_visibility)


async def _resolve_department(db: AsyncSession, value: str | None) -> Department | None:
    if not value:
        return None
    result = await db.execute(
        select(Department).filter((Department.id == value) | (Department.name == value))
    )
    return result.scalar_one_or_none()


async def _resolve_or_create_job(db: AsyncSession, title: str | None) -> Job | None:
    if not title:
        return None
    result = await db.execute(select(Job).filter(Job.title == title))
    job = result.scalar_one_or_none()
    if job:
        return job
    job = Job(title=title)
    db.add(job)
    await db.flush()
    return job


async def _get_current_employee_context(db: AsyncSession, current_user: CurrentUser) -> Employee | None:
    result = await db.execute(
        select(Employee).where(
            (Employee.user_id == current_user.id) | (Employee.email == current_user.email)
        )
    )
    return result.scalar_one_or_none()

@router.get(
    "/me", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_collaborator)],
    summary="Obtenir ses propres informations",
    description="Retourne la fiche collaborateur de l'utilisateur actuellement authentifié."
)
async def get_my_info(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Ses propres informations"""
    emp = await get_or_create_current_employee(current_user, db, extra_options=[
        selectinload(Employee.department), 
        selectinload(Employee.job),
        selectinload(Employee.contracts),
        selectinload(Employee.leaves),
        selectinload(Employee.manager)
    ])
        
    contract_type = emp.job.title if emp.job else None
    salary_val = None
    if emp.contracts:
        active_contract = next((c for c in emp.contracts if c.is_active), emp.contracts[0])
        contract_type = active_contract.contract_type
        salary_val = active_contract.salary
        
    taken_leaves = sum((leave.end_date - leave.start_date).days + 1 for leave in emp.leaves if leave.status == "Approuvé")
    remaining_leaves = max(0, 30 - taken_leaves)
    leave_balance = f"{remaining_leaves} / 30 jours"

    return await _serialize_employee_response(
        db=db,
        current_user=current_user,
        current_employee=emp,
        target_employee=emp,
        scope="self",
        contract_type=contract_type,
        salary=salary_val,
        leave_balance=leave_balance,
    )


@router.get(
    "/me/profile-summary",
    response_model=EmployeeProfileSummaryResponse,
    dependencies=[Depends(require_collaborator)],
    summary="Obtenir le profil enrichi du collaborateur",
)
async def get_my_profile_summary(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    employee = await get_or_create_current_employee(current_user, db, extra_options=[
        selectinload(Employee.department),
        selectinload(Employee.job),
        selectinload(Employee.manager),
        selectinload(Employee.skills).selectinload(EmployeeSkill.skill),
        selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
        selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
        selectinload(Employee.tasks).selectinload(Task.project),
        selectinload(Employee.benefit_enrollments).selectinload(EmployeeBenefit.benefit_plan),
        selectinload(Employee.career_paths).selectinload(CareerPath.target_job),
        selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_department),
        selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_job),
        selectinload(Employee.promotions),
    ])

    pref = (
        await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    ).scalar_one_or_none()

    skills = [
        EmployeeSkillBadge(
            name=item.skill.name,
            category=item.skill.category,
            proficiency_level=item.proficiency_level,
        )
        for item in employee.skills
        if item.skill
    ]

    competencies: list[EmployeeCompetencyItem] = []
    seen: set[str] = set()
    for enrollment in employee.training_enrollments:
        if not enrollment.training or enrollment.training.title in seen:
            continue
        seen.add(enrollment.training.title)
        competencies.append(
            EmployeeCompetencyItem(
                name=enrollment.training.title,
                status=(
                    "done" if enrollment.status == "completed"
                    else "in_progress" if enrollment.status in {"in_progress", "assigned"}
                    else "pending"
                ),
            )
        )
    if employee.job and employee.job.title not in seen:
        competencies.append(
            EmployeeCompetencyItem(
                name=f"Parcours métier · {employee.job.title}",
                status="done" if competencies else "in_progress",
            )
        )

    accomplishments: list[EmployeeAccomplishmentItem] = []
    for task in employee.tasks:
        if task.status == "Terminé":
            accomplishments.append(
                EmployeeAccomplishmentItem(
                    title=f"Tâche finalisée · {task.title}",
                    desc=f"Terminée avec succès dans le cadre du projet {task.project.name if task.project else 'interne'}.",
                    icon="🏆",
                )
            )
        if len(accomplishments) >= 2:
            break
    for enrollment in employee.training_enrollments:
        if enrollment.status == "completed" and enrollment.training:
            accomplishments.append(
                EmployeeAccomplishmentItem(
                    title=f"Formation validée · {enrollment.training.title}",
                    desc=f"Module complété auprès de {enrollment.training.provider or 'Pulse Academy'}.",
                    icon="🎓",
                )
            )
        if len(accomplishments) >= 4:
            break
    if not accomplishments:
        accomplishments.append(
            EmployeeAccomplishmentItem(
                title="Parcours en cours de structuration",
                desc="Les réalisations remonteront ici au fil des tâches terminées et des formations validées.",
                icon="✨",
            )
        )

    active_projects = [
        assignment.project.name
        for assignment in employee.project_assignments
        if assignment.is_active and assignment.project
    ]

    benefits = [
        {
            "plan_name": benefit.benefit_plan.name if benefit.benefit_plan else "Plan",
            "category": benefit.benefit_plan.category if benefit.benefit_plan else "general",
            "provider": benefit.benefit_plan.provider if benefit.benefit_plan else None,
            "status": benefit.status,
            "tier_label": benefit.tier_label,
            "renewal_date_label": benefit.renewal_date.strftime("%d %b %Y") if benefit.renewal_date else None,
            "employer_contribution": benefit.employer_contribution,
            "coverage_summary": benefit.benefit_plan.coverage_summary if benefit.benefit_plan else benefit.notes,
        }
        for benefit in employee.benefit_enrollments
        if benefit.benefit_plan
    ]

    career_paths = [
        {
            "target_title": path.target_title,
            "readiness_level": path.readiness_level,
            "next_step": path.next_step,
            "mentor_name": path.mentor_name,
            "last_reviewed_at_label": path.last_reviewed_at.strftime("%d %b %Y") if path.last_reviewed_at else None,
        }
        for path in employee.career_paths
    ]

    mobility_requests = [
        {
            "request_type": request.request_type,
            "status": request.status,
            "target_department": request.target_department.name if getattr(request, "target_department", None) else None,
            "target_job_title": request.target_job.title if getattr(request, "target_job", None) else None,
            "requested_at_label": request.requested_at.strftime("%d %b %Y") if request.requested_at else None,
            "rationale": request.rationale,
        }
        for request in sorted(employee.mobility_requests, key=lambda item: item.requested_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    ]

    promotions = [
        {
            "previous_job_title": promotion.previous_job_title,
            "new_job_title": promotion.new_job_title,
            "effective_date_label": promotion.effective_date.strftime("%d %b %Y"),
            "notes": promotion.notes,
        }
        for promotion in sorted(employee.promotions, key=lambda item: item.effective_date, reverse=True)
    ]

    return EmployeeProfileSummaryResponse(
        profile_title=(pref.profile_title if pref and pref.profile_title else (employee.job.title if employee.job else "Collaborateur")),
        avatar_data_url=pref.avatar_data_url if pref else None,
        birth_date_label=(pref.birth_date_label if pref and pref.birth_date_label else "Non renseignée"),
        address_label=(pref.address_label if pref and pref.address_label else "Adresse non renseignée"),
        work_location_label=(pref.work_location_label if pref and pref.work_location_label else (" · ".join(filter(None, [employee.department.name if employee.department else None, "Remote friendly"])) if employee.department or active_projects else "Remote friendly")),
        manager_name=f"{employee.manager.first_name} {employee.manager.last_name}" if employee.manager else None,
        skills=skills[:12],
        competencies=competencies[:6],
        accomplishments=accomplishments[:4],
        benefits=benefits[:4],
        career_paths=career_paths[:3],
        mobility_requests=mobility_requests[:3],
        promotions=promotions[:3],
    )

@router.post(
    "/me/change-request", 
    dependencies=[Depends(require_collaborator)],
    summary="Demander une modification de ses informations",
    description="Permet à un collaborateur de soumettre une demande de changement de ses données personnelles à l'équipe RH."
)
def request_info_change(request: ChangeRequest, current_user: CurrentUser = Depends(get_current_user)):
    """Demande de modification de ses infos"""
    return {"status": "request submitted", "data": request}

@router.get(
    "/import/history", 
    response_model=list[ImportHistoryResponse],
    dependencies=[Depends(require_hr)],
    summary="Historique des imports (Admin RH)",
    description="Récupère la liste des derniers fichiers d'employés importés et leur statut d'intégration."
)
async def get_import_history(db: AsyncSession = Depends(get_db)):
    """Historique des imports liés aux employés."""
    from app.models.domain import ImportHistory

    result = await db.execute(
        select(ImportHistory)
        .where(ImportHistory.entity_type.in_(["Employee", "employees"]))
        .order_by(ImportHistory.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()

@router.post(
    "/import", 
    response_model=ImportReport, 
    dependencies=[Depends(require_hr)],
    summary="Import en masse d'employés (Admin RH)",
    description="Permet l'upload d'un fichier CSV ou XLSX contenant une liste d'employés à créer ou mettre à jour.",
    responses={
        400: {"description": "Format de fichier non autorisé (Doit être CSV ou XLSX)."}
    }
)
async def import_employees(
    file: UploadFile = File(...), 
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Import CSV/Excel (upload fichier)"""
    from app.services.import_service import process_csv_import
    from app.schemas.employee import EmployeeImportCSV
    from app.models.domain import Employee
    
    report = await process_csv_import(
        file=file,
        db=db,
        schema_class=EmployeeImportCSV,
        model_class=Employee,
        user_id=current_user.id,
        author_name=f"{current_user.first_name} {current_user.last_name}",
        entity_type="Employee",
        unique_field="id"
    )
    
    # Tracer l'import dans les logs d'audit
    logger.info(f"Audit: User {current_user.id} imported file {file.filename}")
    
    return report

@router.get(
    "/", 
    response_model=EmployeeListResponse, 
    dependencies=[Depends(require_hr)],
    summary="Lister les employés (Admin RH)",
    description="Renvoie une liste paginée d'employés avec des options de filtrage multiples."
)
async def list_employees(
    department: Optional[str] = Query(None, description="Filtrer par nom ou ID de département"),
    status: Optional[str] = Query(None, description="Filtrer par statut (ex: actif, inactif)"),
    contract_type: Optional[str] = Query(None, description="Filtrer par type de contrat"),
    manager_id: Optional[str] = Query(None, description="Filtrer par ID de manager direct"),
    search: Optional[str] = Query(None, description="Recherche textuelle sur le nom ou l'email"),
    page: int = Query(1, ge=1, description="Numéro de la page"),
    page_size: int = Query(20, ge=1, le=1000, description="Nombre de résultats par page"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Liste paginée et filtrable"""
    query = select(Employee).options(
        selectinload(Employee.department),
        selectinload(Employee.job),
        selectinload(Employee.manager),
        selectinload(Employee.tasks),
        selectinload(Employee.attendances),
        selectinload(Employee.contracts),
        selectinload(Employee.engagement_snapshots),
        selectinload(Employee.performance_reviews),
        selectinload(Employee.performance_objectives),
        selectinload(Employee.benefit_enrollments).selectinload(EmployeeBenefit.benefit_plan),
        selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_department),
        selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_job),
        selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
        selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
    )
    if department:
        query = query.join(Department, Department.id == Employee.department_id).filter(
            (Department.id == department) | (Department.name == department)
        )
    if status:
        query = query.filter(Employee.status == status)
    if manager_id:
        query = query.filter(Employee.manager_id == manager_id)
    if search:
        like_value = f"%{search.lower()}%"
        query = query.filter(
            func.lower(func.concat(Employee.first_name, " ", Employee.last_name)).like(like_value) |
            func.lower(Employee.email).like(like_value)
        )
    result = await db.execute(query.limit(page_size).offset((page - 1) * page_size))
    employees_db = result.scalars().all()
    
    count_query = select(func.count(Employee.id))
    if department:
        count_query = count_query.join(Department, Department.id == Employee.department_id).filter(
            (Department.id == department) | (Department.name == department)
        )
    if status:
        count_query = count_query.filter(Employee.status == status)
    if manager_id:
        count_query = count_query.filter(Employee.manager_id == manager_id)
    if search:
        like_value = f"%{search.lower()}%"
        count_query = count_query.filter(
            func.lower(func.concat(Employee.first_name, " ", Employee.last_name)).like(like_value) |
            func.lower(Employee.email).like(like_value)
        )
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    current_employee = await _get_current_employee_context(db, current_user)
    items = []
    for emp in employees_db:
        items.append(
            await _serialize_employee_response(
                db=db,
                current_user=current_user,
                current_employee=current_employee,
                target_employee=emp,
                scope="list",
                contract_type=emp.job.title if emp.job else None,
                salary=None,
                leave_balance=None,
            )
        )
        
    return EmployeeListResponse(items=items, total=total_count, page=page, page_size=page_size)

@router.get(
    "/{id}", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_any_role("hr", "manager"))],
    summary="Récupérer la fiche d'un employé",
    description="Retourne les détails d'un employé spécifique."
)
async def get_employee(
    id: str, 
    request: Request,
    current_user: CurrentUser = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Fiche d'un employé"""
    
    query = select(Employee).options(
        selectinload(Employee.department), 
        selectinload(Employee.job),
        selectinload(Employee.contracts),
        selectinload(Employee.leaves),
        selectinload(Employee.manager),
        selectinload(Employee.tasks),
        selectinload(Employee.attendances),
        selectinload(Employee.engagement_snapshots),
        selectinload(Employee.performance_reviews),
        selectinload(Employee.performance_objectives),
        selectinload(Employee.benefit_enrollments).selectinload(EmployeeBenefit.benefit_plan),
        selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_department),
        selectinload(Employee.mobility_requests).selectinload(MobilityRequest.target_job),
        selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
        selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
    ).filter(Employee.id == id)
    
    result = await db.execute(query)
    emp = result.scalar_one_or_none()
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employé introuvable.")
        
    # Logguer la consultation si ce n'est pas son propre profil
    if emp.email != current_user.email:
        await log_audit_action(
            db=db,
            user_email=current_user.email,
            action=f"a consulté les informations de l'employé {emp.first_name} {emp.last_name}",
            log_type="access",
            request=request,
            critical=False
        )
    
    current_employee = await _get_current_employee_context(db, current_user)

    # Extraire le type de contrat et le salaire
    contract_type = emp.job.title if emp.job else None
    salary_val = None
    if emp.contracts:
        active_contract = next((c for c in emp.contracts if c.is_active), emp.contracts[0])
        contract_type = active_contract.contract_type
        salary_val = active_contract.salary
    
    taken_leaves = sum((leave.end_date - leave.start_date).days + 1 for leave in emp.leaves if leave.status == "Approuvé")
    remaining_leaves = max(0, 30 - taken_leaves)
    leave_balance = f"{remaining_leaves} / 30 jours"

    return await _serialize_employee_response(
        db=db,
        current_user=current_user,
        current_employee=current_employee,
        target_employee=emp,
        scope="detail",
        contract_type=contract_type,
        salary=salary_val,
        leave_balance=leave_balance,
    )

@router.post(
    "/", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_hr)],
    summary="Créer un employé (Admin RH)",
    description="Ajoute un nouvel employé dans la base de données. Réservé aux RH."
)
async def create_employee(
    employee: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
):
    """Créer un employé manuellement"""
    department = await _resolve_department(db, employee.department)
    job = await _resolve_or_create_job(db, employee.job_title)
    new_employee = Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        department_id=department.id if department else None,
        job_id=job.id if job else None,
        status=employee.status,
        manager_id=employee.manager_id,
    )
    db.add(new_employee)
    await db.flush()
    if employee.contract_type:
        db.add(
            Contract(
                employee_id=new_employee.id,
                contract_type=employee.contract_type,
                start_date=new_employee.hire_date,
                salary=employee.salary or 0,
                is_active=True,
            )
        )
    await db.commit()
    synced = await sync_employee_identity(new_employee.id, db)
    result = await db.execute(
        select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.job),
            selectinload(Employee.contracts),
            selectinload(Employee.manager),
            selectinload(Employee.leaves),
        ).filter(Employee.id == synced.id)
    )
    emp = result.scalar_one()
    active_contract = next((c for c in emp.contracts if c.is_active), emp.contracts[0] if emp.contracts else None)
    return EmployeeResponse(
        id=emp.id,
        first_name=emp.first_name,
        last_name=emp.last_name,
        email=emp.email,
        department=emp.department.name if emp.department else None,
        job_title=emp.job.title if emp.job else None,
        status=emp.status,
        contract_type=active_contract.contract_type if active_contract else None,
        manager_id=emp.manager_id,
        salary=active_contract.salary if active_contract else None,
        phone=emp.phone,
        hire_date=emp.hire_date.strftime("%d %B %Y") if emp.hire_date else None,
        manager_name=f"{emp.manager.first_name} {emp.manager.last_name}" if emp.manager else "Aucun manager",
        leave_balance="30 / 30 jours",
    )

@router.put(
    "/{id}", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_hr)],
    summary="Modifier un employé (Admin RH)",
    description="Met à jour unitairement les informations d'un employé existant."
)
async def update_employee(
    id: str,
    employee: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Modifier un employé"""
    result = await db.execute(
        select(Employee).options(selectinload(Employee.contracts), selectinload(Employee.department), selectinload(Employee.job), selectinload(Employee.manager)).filter(Employee.id == id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Employé introuvable.")

    if employee.first_name is not None:
        existing.first_name = employee.first_name
    if employee.last_name is not None:
        existing.last_name = employee.last_name
    if employee.email is not None:
        existing.email = employee.email
    if employee.status is not None:
        existing.status = employee.status
    if employee.manager_id is not None:
        existing.manager_id = employee.manager_id
    if employee.department is not None:
        department = await _resolve_department(db, employee.department)
        existing.department_id = department.id if department else None
    if employee.job_title is not None:
        job = await _resolve_or_create_job(db, employee.job_title)
        existing.job_id = job.id if job else None

    active_contract = next((contract for contract in existing.contracts if contract.is_active), None)
    if employee.contract_type is not None or employee.salary is not None:
        if not active_contract:
            active_contract = Contract(
                employee_id=existing.id,
                contract_type=employee.contract_type or "CDI",
                start_date=existing.hire_date,
                salary=employee.salary or 0,
                is_active=True,
            )
            db.add(active_contract)
        else:
            if employee.contract_type is not None:
                active_contract.contract_type = employee.contract_type
            if employee.salary is not None:
                active_contract.salary = employee.salary

    await db.commit()
    await sync_employee_identity(existing.id, db)
    refreshed = await db.execute(
        select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.job),
            selectinload(Employee.contracts),
            selectinload(Employee.leaves),
            selectinload(Employee.manager),
        ).filter(Employee.id == existing.id)
    )
    emp = refreshed.scalar_one()
    active_contract = next((c for c in emp.contracts if c.is_active), emp.contracts[0] if emp.contracts else None)
    return EmployeeResponse(
        id=emp.id,
        first_name=emp.first_name,
        last_name=emp.last_name,
        email=emp.email,
        department=emp.department.name if emp.department else None,
        status=emp.status,
        contract_type=active_contract.contract_type if active_contract else (emp.job.title if emp.job else None),
        manager_id=emp.manager_id,
        salary=active_contract.salary if active_contract else None,
        phone=emp.phone,
        hire_date=emp.hire_date.strftime("%d %B %Y") if emp.hire_date else None,
        manager_name=f"{emp.manager.first_name} {emp.manager.last_name}" if emp.manager else "Aucun manager",
        leave_balance=None,
        job_title=emp.job.title if emp.job else None,
    )

@router.delete(
    "/{id}", 
    dependencies=[Depends(require_hr)],
    summary="Désactiver un employé (Admin RH)",
    description="Marque l'employé comme inactif. Ne supprime pas physiquement la donnée de la base pour des raisons d'historisation."
)
async def disable_employee(id: str, db: AsyncSession = Depends(get_db)):
    """Désactiver un employé"""
    employee = await db.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employé introuvable.")
    employee.status = "inactif"
    await db.commit()
    if employee.user_id:
        try:
            from app.services.keycloak_admin_service import keycloak_admin_service
            await keycloak_admin_service.set_enabled(employee.user_id, False)
        except Exception as exc:
            logger.warning("Impossible de désactiver le compte Keycloak pour %s: %s", employee.email, exc)
    return {"status": "Disabled", "id": id}
