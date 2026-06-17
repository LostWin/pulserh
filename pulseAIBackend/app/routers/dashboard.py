import logging
from typing import Optional
from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.domain import Department, Employee, Document, Interview, ProjectAssignment, TrainingEnrollment, EmployeeBenefit
from app.schemas.dashboard import (
    CollaboratorDashboardResponse,
    DirectionDashboardResponse,
    HeadcountResponse,
    KPIsResponse,
    ManagerDashboardResponse,
    RHDashboardResponse,
)
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_collaborator, require_hr, require_any_role
from app.services.current_employee_service import get_or_create_current_employee
from app.services.hr_analytics_service import (
    benefits_status_for_employee,
    build_interview_index,
    build_turnover_projection,
    current_project_names,
    department_engagement,
    employee_performance_score,
    employee_risk_payload,
    employee_tenure_label,
    interviews_to_schedule,
    next_benefits_enrollment_label,
)
from app.services.risk_predictor import risk_predictor

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)

# Dépendances RBAC communes
kpi_roles = require_any_role("hr", "manager", "director")
hr_director_roles = require_any_role("hr", "director")
manager_roles = require_any_role("manager")
director_roles = require_any_role("director")

# Classe utilitaire pour injecter facilement les filtres communs
class DashboardFilters:
    def __init__(
        self,
        period_start: Optional[date] = Query(None, description="Date de début"),
        period_end: Optional[date] = Query(None, description="Date de fin"),
        department_id: Optional[str] = Query(None, description="Filtre sur un département"),
        entity_id: Optional[str] = Query(None, description="Filtre sur une entité légale")
    ):
        self.period_start = period_start
        self.period_end = period_end
        self.department_id = department_id
        self.entity_id = entity_id

@router.get("/kpis", response_model=KPIsResponse, dependencies=[Depends(kpi_roles)])
async def get_kpis(
    filters: DashboardFilters = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """KPIs consolidés (effectifs, turnover, absentéisme)"""
    query = select(Employee).options(
        selectinload(Employee.attendances),
        selectinload(Employee.contracts),
        selectinload(Employee.tasks),
        selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
        selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
        selectinload(Employee.engagement_snapshots),
    )
    if "manager" in current_user.roles and "hr" not in current_user.roles and "director" not in current_user.roles:
        manager = await _get_current_employee(current_user, db)
        query = query.where(Employee.manager_id == manager.id)
    employees = (await db.execute(query)).scalars().all()
    active_employees = [employee for employee in employees if employee.status != "inactif"]
    risk_scores = []
    for employee in active_employees:
        pred = await risk_predictor.predict(employee, db)
        risk_scores.append(pred["score_pct"])
    absent_days = 0
    attendance_days = 0
    salaries = []
    for employee in active_employees:
        attendance_days += len(employee.attendances)
        absent_days += sum(1 for attendance in employee.attendances if (attendance.status or "").lower() == "absent")
        active_contract = next((contract for contract in employee.contracts if contract.is_active), None)
        if active_contract and active_contract.salary is not None:
            salaries.append(active_contract.salary)
    return KPIsResponse(
        headcount=len(active_employees),
        turnover_rate=_turnover_prediction_from_risks(risk_scores, len(active_employees)),
        absenteeism_rate=round((absent_days / max(attendance_days, 1)) * 100, 2),
        avg_salary=round(sum(salaries) / len(salaries), 2) if salaries else 0.0,
    )

@router.get("/headcount", response_model=HeadcountResponse, dependencies=[Depends(hr_director_roles)])
async def get_headcount(filters: DashboardFilters = Depends(), db: AsyncSession = Depends(get_db)):
    """Effectifs par département/contrat/site"""
    employees = (
        await db.execute(
            select(Employee).options(selectinload(Employee.department), selectinload(Employee.contracts))
        )
    ).scalars().all()
    active_employees = [employee for employee in employees if employee.status != "inactif"]
    by_department_counter: dict[str, int] = {}
    by_contract_counter: dict[str, int] = {}
    by_site_counter: dict[str, int] = {}
    for employee in active_employees:
        department_name = employee.department.name if employee.department else "Non assigné"
        by_department_counter[department_name] = by_department_counter.get(department_name, 0) + 1
        active_contract = next((contract for contract in employee.contracts if contract.is_active), None)
        contract_label = active_contract.contract_type if active_contract else "Non défini"
        by_contract_counter[contract_label] = by_contract_counter.get(contract_label, 0) + 1
        site_label = employee.department.name if employee.department else "Remote"
        by_site_counter[site_label] = by_site_counter.get(site_label, 0) + 1
    return HeadcountResponse(
        by_department=[{"department": key, "count": value} for key, value in sorted(by_department_counter.items())],
        by_contract_type=[{"contract": key, "count": value} for key, value in sorted(by_contract_counter.items())],
        by_site=[{"site": key, "count": value} for key, value in sorted(by_site_counter.items())],
    )

@router.get("/absenteeism", dependencies=[Depends(kpi_roles)])
async def get_absenteeism(
    filters: DashboardFilters = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Taux d'absentéisme"""
    query = select(Employee).options(selectinload(Employee.attendances), selectinload(Employee.department))
    if "manager" in current_user.roles and "hr" not in current_user.roles and "director" not in current_user.roles:
        manager = await _get_current_employee(current_user, db)
        query = query.where(Employee.manager_id == manager.id)
    employees = (await db.execute(query)).scalars().all()
    details = []
    total_absent = 0
    total_days = 0
    for employee in employees:
        attendances = employee.attendances
        absent = sum(1 for attendance in attendances if (attendance.status or "").lower() == "absent")
        total = len(attendances)
        total_absent += absent
        total_days += total
        if total:
            details.append(
                {
                    "employee_id": employee.id,
                    "employee": f"{employee.first_name} {employee.last_name}",
                    "department": employee.department.name if employee.department else "Non assigné",
                    "absenteeism_rate": round((absent / total) * 100, 2),
                }
            )
    return {"status": "ok", "absenteeism_rate": round((total_absent / max(total_days, 1)) * 100, 2), "details": details[:25]}

@router.get("/salary-mass", dependencies=[Depends(hr_director_roles)])
async def get_salary_mass(filters: DashboardFilters = Depends(), db: AsyncSession = Depends(get_db)):
    """Masse salariale et projections"""
    employees = (
        await db.execute(
            select(Employee).options(selectinload(Employee.contracts), selectinload(Employee.training_enrollments))
        )
    ).scalars().all()
    salaries = []
    projected_uplift = 0.0
    for employee in employees:
        contract = next((item for item in employee.contracts if item.is_active and item.salary is not None), None)
        if not contract:
            continue
        salaries.append(contract.salary)
        projected_uplift += contract.salary * 0.018
        if any(enrollment.mandatory and enrollment.status != "completed" for enrollment in employee.training_enrollments):
            projected_uplift += contract.salary * 0.004
    total_mass = round(sum(salaries), 2)
    return {"status": "ok", "total_mass": total_mass, "projected_mass": round(total_mass + projected_uplift, 2)}

@router.get("/age-pyramid", dependencies=[Depends(hr_director_roles)])
async def get_age_pyramid(filters: DashboardFilters = Depends(), db: AsyncSession = Depends(get_db)):
    """Données pour pyramide des âges"""
    employees = (await db.execute(select(Employee).where(Employee.status != "inactif"))).scalars().all()
    current_year = date.today().year
    bins = [
        {"range": "<25", "count": 0},
        {"range": "25-34", "count": 0},
        {"range": "35-44", "count": 0},
        {"range": "45-54", "count": 0},
        {"range": "55+", "count": 0},
    ]
    for employee in employees:
        synthetic_age = 22 + min(35, max(0, current_year - employee.hire_date.year))
        if synthetic_age < 25:
            bins[0]["count"] += 1
        elif synthetic_age < 35:
            bins[1]["count"] += 1
        elif synthetic_age < 45:
            bins[2]["count"] += 1
        elif synthetic_age < 55:
            bins[3]["count"] += 1
        else:
            bins[4]["count"] += 1
    return {"status": "ok", "bins": bins}




def _turnover_prediction_from_risks(risk_scores: list[float], headcount: int) -> float:
    if headcount <= 0 or not risk_scores:
        return 0.0
    avg_risk = sum(risk_scores) / len(risk_scores)
    return round(min(18.0, 2.8 + (avg_risk / 100) * 12 + max(0, (65 - (100 - avg_risk)) * 0.04)), 1)


async def _get_current_employee(current_user: CurrentUser, db: AsyncSession) -> Employee:
    return await get_or_create_current_employee(
        current_user,
        db,
        extra_options=[
            selectinload(Employee.department),
            selectinload(Employee.job),
            selectinload(Employee.contracts),
            selectinload(Employee.leaves),
            selectinload(Employee.tasks),
            selectinload(Employee.attendances),
            selectinload(Employee.manager),
            selectinload(Employee.subordinates),
            selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
            selectinload(Employee.engagement_snapshots),
            selectinload(Employee.performance_objectives),
            selectinload(Employee.performance_reviews),
            selectinload(Employee.benefit_enrollments).selectinload(EmployeeBenefit.benefit_plan),
            selectinload(Employee.career_paths),
            selectinload(Employee.mobility_requests),
        ],
    )


def _format_relative_days(day_count: int) -> str:
    if day_count <= 0:
        return "Aujourd'hui"
    if day_count == 1:
        return "Demain"
    return f"Dans {day_count} j"


def _previous_month(year: int, month: int) -> tuple[int, int]:
    return (year - 1, 12) if month == 1 else (year, month - 1)


def _month_window(month_count: int = 6) -> list[tuple[int, int]]:
    current = date.today().replace(day=1)
    items: list[tuple[int, int]] = []
    year, month = current.year, current.month
    for _ in range(month_count):
        items.append((year, month))
        year, month = _previous_month(year, month)
    return list(reversed(items))


def _month_label(month: int) -> str:
    labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    return labels[month - 1]


def _build_manager_trend(team: list[Employee], avg_engagement: int, base_risk: int) -> list[dict]:
    snapshot_index: dict[tuple[int, int], list[int]] = {}
    for employee in team:
        ordered_snapshots = sorted(
            employee.engagement_snapshots,
            key=lambda item: item.captured_at or datetime.min.replace(tzinfo=timezone.utc),
        )
        for snapshot in ordered_snapshots:
            captured_at = snapshot.captured_at or datetime.now(timezone.utc)
            snapshot_index.setdefault((captured_at.year, captured_at.month), []).append(snapshot.score)

    carry_engagement = avg_engagement or 72
    trend: list[dict] = []
    for year, month in _month_window(6):
        scores = snapshot_index.get((year, month), [])
        if scores:
            engagement = round(sum(scores) / len(scores))
            carry_engagement = engagement
        else:
            engagement = carry_engagement

        risk = max(8, min(55, round((100 - engagement) * 0.52 + max(base_risk - 35, 0) * 0.28)))
        trend.append({
            "month": _month_label(month),
            "engagement": engagement,
            "risque": risk,
        })
    return trend


def _employee_tenure_label(employee: Employee) -> str:
    if not employee.hire_date:
        return "Ancienneté inconnue"
    return employee_tenure_label(employee)


def _manager_risk_factors(employee: Employee) -> list[dict[str, int | str]]:
    overdue_tasks = sum(
        1 for task in employee.tasks
        if task.due_date and task.due_date < date.today() and task.status != "Terminé"
    )
    absences_30 = sum(
        1 for attendance in employee.attendances
        if attendance.date and attendance.date >= date.today() - timedelta(days=30) and (attendance.status or "").lower() == "absent"
    )
    factors = [
        {"label": "Charge de travail", "value": min(95, 20 + overdue_tasks * 18)},
        {"label": "Assiduité", "value": min(95, 15 + absences_30 * 16)},
        {"label": "Stabilité opérationnelle", "value": min(95, 25 + (3 if employee.status != "actif" else 0) * 10)},
        {"label": "Perspectives d'évolution", "value": min(95, 28 + (len(employee.contracts) == 0) * 18)},
        {"label": "Équilibre vie pro/perso", "value": min(95, 22 + overdue_tasks * 12 + absences_30 * 6)},
        {"label": "Reconnaissance", "value": min(95, 24 + max(0, 6 - len(employee.tasks)) * 4)},
    ]
    return sorted(factors, key=lambda item: item["value"], reverse=True)


def _manager_recommendation(top_factor: str) -> str:
    mapping = {
        "Charge de travail": "Rééquilibrer la charge de travail et prioriser les livrables les plus critiques.",
        "Assiduité": "Planifier un point rapproché pour comprendre les causes des absences répétées.",
        "Stabilité opérationnelle": "Sécuriser les conditions opérationnelles et clarifier les attentes à court terme.",
        "Perspectives d'évolution": "Co-construire un plan d’évolution et de développement avec le collaborateur.",
        "Équilibre vie pro/perso": "Proposer davantage de flexibilité et ajuster le rythme des livraisons.",
        "Reconnaissance": "Mettre en place un feedback plus fréquent et valoriser les contributions visibles.",
    }
    return mapping.get(top_factor, "Prévoir un échange managérial et ajuster le plan d'accompagnement.")


async def _manager_team_member_payload(employee: Employee, db: AsyncSession) -> dict:
    risk_payload = await risk_predictor.predict(employee, db)
    factors = risk_payload["factors"]
    risk_score = round(risk_payload["score_pct"])
    risk = "high" if risk_payload["level"] == "red" else "medium" if risk_payload["level"] == "orange" else "low"
    engagement = risk_payload["engagement"]
    delta = 3 if risk == "low" else (-6 if risk == "medium" else -12)

    overdue_tasks = sum(
        1 for task in employee.tasks
        if task.due_date and task.due_date < date.today() and task.status != "Terminé"
    )
    absences_30 = sum(
        1 for attendance in employee.attendances
        if attendance.date and attendance.date >= date.today() - timedelta(days=30) and (attendance.status or "").lower() == "absent"
    )
    if overdue_tasks >= 2:
        signal = f"{overdue_tasks} tâches en retard détectées."
    elif absences_30 >= 2:
        signal = f"{absences_30} absences sur les 30 derniers jours."
    else:
        signal = "Situation stable, aucun signal critique récent."

    due_dates = [task.due_date for task in employee.tasks if task.due_date and task.status != "Terminé"]
    next_due_date = min(due_dates) if due_dates else None
    last_active = _format_relative_days((next_due_date - date.today()).days) if next_due_date else "Aujourd'hui"
    prioritized_objective = next(
        (
            objective for objective in sorted(
                employee.performance_objectives,
                key=lambda item: (item.status != "in_progress", -(item.progress_pct or 0)),
            )
            if objective.status != "completed"
        ),
        None,
    )

    return {
        "id": employee.id,
        "name": f"{employee.first_name} {employee.last_name}",
        "title": employee.job.title if employee.job else "Collaborateur",
        "department": risk_payload["department"],
        "engagement": engagement,
        "risk": risk,
        "delta": delta,
        "tenure": _employee_tenure_label(employee),
        "last_active": last_active,
        "signal": signal,
        "risk_score": risk_score,
        "factors": factors,
        "recommendation": risk_payload["recommendation"],
        "performance_score": employee_performance_score(employee),
        "focus_objective_title": prioritized_objective.title if prioritized_objective else None,
        "focus_objective_progress_pct": prioritized_objective.progress_pct if prioritized_objective else None,
        "benefits_status": benefits_status_for_employee(employee),
        "mobility_status": next(
            (request.status for request in sorted(employee.mobility_requests, key=lambda item: item.requested_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)),
            "none",
        ),
    }


@router.get("/collaborateur-summary", response_model=CollaboratorDashboardResponse, dependencies=[Depends(require_collaborator)])
async def get_collaborator_dashboard_summary(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    employee = await _get_current_employee(current_user, db)
    documents_result = await db.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    all_documents = documents_result.scalars().all()
    visible_documents = [
        document for document in all_documents
        if any(role in (document.allowed_roles or []) for role in current_user.roles)
        or "hr" in current_user.roles
        or "admin" in current_user.roles
    ]

    approved_leaves = [leave for leave in employee.leaves if leave.status == "Approuvé"]
    paid_used = sum(
        max(0, (leave.end_date - leave.start_date).days + 1)
        for leave in approved_leaves
        if "pay" in (leave.leave_type or "").lower() or "cong" in (leave.leave_type or "").lower()
    )
    leave_total_balance = 30
    leave_current_balance = max(0, leave_total_balance - paid_used)

    onboarding = [
        {"label": "Compléter le profil", "done": bool(employee.phone), "date_label": employee.hire_date.strftime("%d %b") if employee.hire_date else None},
        {"label": "Signer le contrat électronique", "done": any(contract.is_active for contract in employee.contracts), "date_label": employee.hire_date.strftime("%d %b") if employee.hire_date else None},
        {"label": "Configurer le poste de travail", "done": len(employee.tasks) > 0 or len(employee.project_assignments) > 0, "date_label": None},
        {"label": "Formation sécurité & RGPD", "done": any(enrollment.mandatory and enrollment.status == "completed" for enrollment in employee.training_enrollments), "date_label": None},
        {"label": "Rencontrer son manager", "done": employee.manager is not None, "date_label": None},
    ]

    recent_documents = [
        {
            "id": document.id,
            "name": document.name,
            "type": document.type,
            "date": document.created_at.strftime("%d %b %Y"),
            "size": document.size,
        }
        for document in visible_documents[:5]
    ]

    compliance_docs = sum(
        1 for document in visible_documents
        if any(keyword in (document.type or "").lower() for keyword in ["policy", "compliance", "rgpd", "sécurité"])
    )
    documents_pending = sum(1 for document in visible_documents if "attente" in (document.rag_status or "").lower())
    performance_score = employee_performance_score(employee)
    completed_trainings = sum(1 for enrollment in employee.training_enrollments if enrollment.status == "completed")
    active_projects = current_project_names(employee)
    active_benefit = next(
        (benefit for benefit in employee.benefit_enrollments if benefit.status in {"active", "eligible", "enrolled"}),
        employee.benefit_enrollments[0] if employee.benefit_enrollments else None,
    )
    primary_benefit_label = active_benefit.benefit_plan.name if active_benefit and active_benefit.benefit_plan else None
    prioritized_objective = next(
        (
            objective for objective in sorted(
                employee.performance_objectives,
                key=lambda item: (item.status != "in_progress", -(item.progress_pct or 0)),
            )
            if objective.status != "completed"
        ),
        None,
    )
    performance_target_label = (
        f"{prioritized_objective.title} · {prioritized_objective.progress_pct}%"
        if prioritized_objective
        else f"{max(1, completed_trainings)} formation(s) validée(s)"
    )
    career_focus = next(
        (
            path for path in sorted(
                employee.career_paths,
                key=lambda item: item.last_reviewed_at or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
        ),
        None,
    )
    latest_mobility = next(
        (
            request for request in sorted(
                employee.mobility_requests,
                key=lambda item: item.requested_at or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
        ),
        None,
    )

    return {
        "summary": {
            "first_name": employee.first_name,
            "leave_current_balance": leave_current_balance,
            "leave_total_balance": leave_total_balance,
            "benefits_status": benefits_status_for_employee(employee),
            "next_benefits_enrollment": next_benefits_enrollment_label(employee=employee),
            "primary_benefit_label": primary_benefit_label,
            "performance_score": performance_score,
            "performance_target_label": performance_target_label,
            "career_focus_title": career_focus.target_title if career_focus else None,
            "mobility_status": latest_mobility.status if latest_mobility else "Aucune demande",
            "documents_total": len(visible_documents),
            "documents_pending": documents_pending,
            "policies_total": compliance_docs,
            "compliance_score": min(100, 65 + compliance_docs * 6 + completed_trainings * 4 + min(len(active_projects), 3) * 3),
        },
        "onboarding": onboarding,
        "recent_documents": recent_documents,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/manager-summary", response_model=ManagerDashboardResponse, dependencies=[Depends(manager_roles)])
async def get_manager_dashboard_summary(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manager = await _get_current_employee(current_user, db)
    team_result = await db.execute(
        select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.job),
            selectinload(Employee.tasks),
            selectinload(Employee.attendances),
        selectinload(Employee.contracts),
            selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
            selectinload(Employee.engagement_snapshots),
            selectinload(Employee.performance_objectives),
            selectinload(Employee.benefit_enrollments).selectinload(EmployeeBenefit.benefit_plan),
            selectinload(Employee.mobility_requests),
        ).filter(Employee.manager_id == manager.id)
    )
    team = team_result.scalars().all()

    team_payload = [await _manager_team_member_payload(employee, db) for employee in team]
    avg_engagement = round(sum(member["engagement"] for member in team_payload) / len(team_payload)) if team_payload else 0
    at_risk = [member for member in team_payload if member["risk"] != "low"]
    interviews_result = await db.execute(select(Interview).where(Interview.manager_id == manager.id))
    manager_interviews = interviews_result.scalars().all()
    interviews_due = interviews_to_schedule(team, manager_interviews)
    mobility_requests_open = sum(
        1
        for employee in team
        for request in employee.mobility_requests
        if request.status in {"draft", "submitted", "reviewed"}
    )

    base_engagement = avg_engagement or 72
    base_risk = round(sum(member["risk_score"] for member in team_payload) / len(team_payload)) if team_payload else 28
    trend = _build_manager_trend(team, base_engagement, base_risk)

    alerts = []
    for member in at_risk[:4]:
        alerts.append({
            "id": member["id"],
            "level": "high" if member["risk"] == "high" else "medium",
            "text": f"{member['name']} — {member['signal']}",
            "time": "Mis à jour aujourd'hui",
            "route": "/manager/alertes",
        })
    if not alerts:
        alerts.append({
            "id": "team-ok",
            "level": "low",
            "text": "Aucun signal critique détecté sur l'équipe.",
            "time": "Mis à jour aujourd'hui",
            "route": "/manager/alertes",
        })

    return {
        "summary": {
            "team_size": len(team_payload),
            "avg_engagement": avg_engagement,
            "at_risk_count": len(at_risk),
            "interviews_to_schedule": interviews_due,
            "mobility_requests_open": mobility_requests_open,
        },
        "trend": trend,
        "team": sorted(team_payload, key=lambda member: member["risk_score"], reverse=True),
        "alerts": alerts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/rh-summary", response_model=RHDashboardResponse, dependencies=[Depends(require_hr)])
async def get_rh_dashboard_summary(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Agrégat backend pour conserver le rendu actuel du dashboard RH.

    Sources:
    - effectif: réel
    - répartition par département: réelle
    - risque: réel via tâches, absences, formations obligatoires et signaux d'engagement
    - engagement: réel si snapshots disponibles, sinon formule déterministe basée sur signaux RH
    - turnover prédit: projection heuristique backend à partir des scores de risque réels
    """
    department_result = await db.execute(
        select(Department).options(selectinload(Department.employees))
    )
    departments = department_result.scalars().all()

    employee_result = await db.execute(
        select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.job),
            selectinload(Employee.attendances),
            selectinload(Employee.tasks),
            selectinload(Employee.contracts),
            selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
            selectinload(Employee.engagement_snapshots),
        )
    )
    employees = employee_result.scalars().all()

    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    employees_by_department: dict[str, list[Employee]] = {}
    for employee in employees:
      if employee.department_id:
        employees_by_department.setdefault(employee.department_id, []).append(employee)

    department_items = []
    total_headcount = 0
    weighted_engagement_sum = 0
    active_risks = 0
    risk_scores: list[float] = []

    known_department_ids = set()
    for department in departments:
        known_department_ids.add(department.id)
        department_employees = employees_by_department.get(department.id, [])
        headcount = len([employee for employee in department_employees if employee.status != "inactif"])

        overdue_tasks = 0
        repeated_absences = 0
        for employee in department_employees:
            overdue_tasks += sum(
                1 for task in employee.tasks
                if task.due_date and task.due_date < today and task.status != "Terminé"
            )
            repeated_absences += sum(
                1 for attendance in employee.attendances
                if attendance.date and attendance.date >= thirty_days_ago and (attendance.status or "").lower() == "absent"
            )

        risk = 0
        if headcount > 0:
            risk_payloads = []
            for employee in department_employees:
                if employee.status != "inactif":
                    risk_payloads.append(await risk_predictor.predict(employee, db))
            risk_scores.extend([payload["score_pct"] for payload in risk_payloads])
            risk = round(sum(payload["score_pct"] for payload in risk_payloads) / len(risk_payloads)) if risk_payloads else max(3, min(38, round((((overdue_tasks * 1.8) + repeated_absences) / headcount) * 8)))
        else:
            risk = 0

        engagement = department_engagement([employee for employee in department_employees if employee.status != "inactif"])
        metrics_source = {
            "headcount": "real",
            "risk": "real" if headcount > 0 else "fallback",
            "engagement": "real" if any(employee.engagement_snapshots for employee in department_employees) else "derived",
        }

        department_items.append({
            "id": department.id,
            "name": department.name,
            "headcount": headcount,
            "engagement": engagement,
            "risk": risk,
            "metrics_source": metrics_source,
        })

        total_headcount += headcount
        weighted_engagement_sum += engagement * headcount
        active_risks += round((risk / 100) * headcount)

    orphan_employees = [employee for employee in employees if not employee.department_id or employee.department_id not in known_department_ids]
    if orphan_employees:
        headcount = len(orphan_employees)
        orphan_payloads = []
        for employee in orphan_employees:
            orphan_payloads.append(await risk_predictor.predict(employee, db))
        risk_scores.extend([payload["score_pct"] for payload in orphan_payloads])
        risk = round(sum(payload["score_pct"] for payload in orphan_payloads) / len(orphan_payloads)) if orphan_payloads else max(5, min(22, 8 + headcount))
        engagement = department_engagement(orphan_employees)
        department_items.append({
            "id": "unassigned",
            "name": "Non assigné",
            "headcount": headcount,
            "engagement": engagement,
            "risk": risk,
            "metrics_source": {
                "headcount": "real",
                "risk": "real" if orphan_payloads else "fallback",
                "engagement": "real" if any(employee.engagement_snapshots for employee in orphan_employees) else "derived",
            },
        })
        total_headcount += headcount
        weighted_engagement_sum += engagement * headcount
        active_risks += round((risk / 100) * headcount)

    department_items.sort(key=lambda item: item["headcount"], reverse=True)

    global_engagement = round(weighted_engagement_sum / total_headcount) if total_headcount else 0

    turnover_predicted = _turnover_prediction_from_risks(risk_scores, total_headcount)

    return {
        "summary": {
            "headcount": total_headcount,
            "global_engagement": global_engagement,
            "turnover_predicted": turnover_predicted,
            "active_risks": active_risks,
        },
        "departments": department_items,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/direction-summary", response_model=DirectionDashboardResponse, dependencies=[Depends(director_roles)])
async def get_direction_dashboard_summary(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    department_result = await db.execute(
        select(Department).options(selectinload(Department.employees))
    )
    departments = department_result.scalars().all()
    employee_result = await db.execute(
        select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.job),
            selectinload(Employee.attendances),
            selectinload(Employee.tasks),
            selectinload(Employee.contracts),
            selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
            selectinload(Employee.engagement_snapshots),
        )
    )
    employees = employee_result.scalars().all()

    department_items = []
    total_headcount = 0
    engagement_sum = 0
    active_risks = 0
    risk_scores: list[float] = []
    active_contract_salaries: list[float] = []
    training_total = 0
    training_completed = 0
    interviews = (await db.execute(select(Interview))).scalars().all()
    interview_index = build_interview_index(interviews)
    for department in departments:
        scoped = [employee for employee in employees if employee.department_id == department.id]
        headcount = len(scoped)
        total_headcount += headcount
        department_risks = []
        for employee in scoped:
            department_risks.append(await risk_predictor.predict(employee, db))
        risk = round(sum(payload["score_pct"] for payload in department_risks) / len(department_risks)) if department_risks else 0
        active_risks += risk
        risk_scores.extend(payload["score_pct"] for payload in department_risks)
        engagement = department_engagement(scoped)
        engagement_sum += engagement * headcount
        for employee in scoped:
            training_total += len(employee.training_enrollments)
            training_completed += sum(1 for enrollment in employee.training_enrollments if enrollment.status == "completed")
            for contract in employee.contracts:
                if contract.is_active and contract.salary is not None:
                    active_contract_salaries.append(contract.salary)
        department_items.append(
            {
                "id": department.id,
                "name": department.name,
                "headcount": headcount,
                "engagement": engagement,
            }
        )

    global_engagement = round(engagement_sum / max(total_headcount, 1))
    if len(risk_scores) >= 6:
        monthly_scores = [round(score) for score in risk_scores[:6]]
    else:
        monthly_scores = [round(score) for score in risk_scores]
        monthly_scores.extend(
            [round(sum(risk_scores) / len(risk_scores)) if risk_scores else 32] * max(0, 6 - len(monthly_scores))
        )
    monthly_projection = build_turnover_projection(monthly_scores[:6], total_headcount)
    average_salary = round(sum(active_contract_salaries) / len(active_contract_salaries), 2) if active_contract_salaries else 42000.0
    training_completion_rate = training_completed / training_total if training_total else 0.55
    interview_coverage_rate = (
        sum(1 for employee in employees if interview_index.get(employee.id)) / max(total_headcount, 1)
    ) if total_headcount else 0
    mitigation_rate = min(0.42, 0.12 + training_completion_rate * 0.18 + interview_coverage_rate * 0.12 + max(0, global_engagement - 65) / 300)
    departure_cost_k = (average_salary * 0.35) / 1000
    turnover_saved = []
    for index, month in enumerate(monthly_projection, start=1):
        avoided_departures = max(1, round(month["projected_departures"] * mitigation_rate))
        savings = round(avoided_departures * departure_cost_k, 1)
        turnover_saved.append(
            {
                "month": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"][index - 1],
                "economie": savings,
                "depart": month["projected_departures"],
            }
        )

    alerts = sorted(department_items, key=lambda item: item["engagement"])[:3]
    strategic_alerts = [
        {
            "level": "high" if item["engagement"] < 65 else "medium",
            "text": f"Département {item['name']} sous surveillance ({item['engagement']}/100).",
            "impact": f"≈ {round(max(18, item['headcount'] * departure_cost_k * 0.18), 1)} k€ de risque turnover",
        }
        for item in alerts
    ]

    ai_investment_k = round(max(8.0, total_headcount * 0.18 + len(interviews) * 0.04 + training_total * 0.02), 1)
    roi_ia = round(sum(item["economie"] for item in turnover_saved) / max(ai_investment_k, 1), 1)

    return {
        "summary": {
            "global_engagement": global_engagement,
            "turnover_saved_total": round(sum(item["economie"] for item in turnover_saved), 1),
            "roi_ia": roi_ia,
            "headcount": total_headcount,
        },
        "turnover_saved": turnover_saved,
        "departments": sorted(department_items, key=lambda item: item["engagement"]),
        "alerts": strategic_alerts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
