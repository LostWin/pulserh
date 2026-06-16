from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from statistics import mean
from typing import Iterable

from app.models.domain import Employee, Interview


def days_inclusive(start_date: date, end_date: date) -> int:
    return max(0, (end_date - start_date).days + 1)


def employee_tenure_label(employee: Employee) -> str:
    if not employee.hire_date:
        return "Ancienneté inconnue"
    days = max(1, (date.today() - employee.hire_date).days)
    if days < 365:
        months = max(1, round(days / 30))
        return f"{months} mois"
    years = round(days / 365)
    return f"{years} ans"


def current_project_names(employee: Employee) -> list[str]:
    return [
        assignment.project.name
        for assignment in employee.project_assignments
        if assignment.is_active and assignment.project
    ]


def employee_performance_score(employee: Employee) -> float:
    task_scores = [task.evaluation_score for task in employee.tasks if task.evaluation_score is not None]
    training_scores = [enrollment.score for enrollment in employee.training_enrollments if enrollment.score is not None]
    if task_scores or training_scores:
        values = [*task_scores, *training_scores]
        return round(sum(values) / len(values), 1)

    completed_tasks = sum(1 for task in employee.tasks if task.status == "Terminé")
    total_tasks = len(employee.tasks)
    completed_mandatory = sum(
        1 for enrollment in employee.training_enrollments
        if enrollment.mandatory and enrollment.status == "completed"
    )
    baseline = 3.4 + min(1.1, completed_tasks * 0.12) + min(0.4, completed_mandatory * 0.15)
    if total_tasks:
        baseline += min(0.5, completed_tasks / total_tasks * 0.5)
    return round(min(5.0, baseline), 1)


def employee_engagement_score(employee: Employee, as_of: date | None = None) -> int:
    as_of = as_of or date.today()
    snapshot_scores = [snapshot.score for snapshot in employee.engagement_snapshots]
    base = round(mean(snapshot_scores[-3:])) if snapshot_scores else 72

    overdue_tasks = sum(
        1 for task in employee.tasks
        if task.due_date and task.due_date < as_of and task.status != "Terminé"
    )
    absences_30 = sum(
        1 for attendance in employee.attendances
        if attendance.date and attendance.date >= as_of - timedelta(days=30) and (attendance.status or "").lower() == "absent"
    )
    mandatory_overdue = sum(
        1 for enrollment in employee.training_enrollments
        if enrollment.mandatory and enrollment.due_date and enrollment.due_date < as_of and enrollment.status != "completed"
    )
    completed_trainings = sum(1 for enrollment in employee.training_enrollments if enrollment.status == "completed")
    active_projects = sum(1 for assignment in employee.project_assignments if assignment.is_active)

    score = base
    score -= min(18, overdue_tasks * 5)
    score -= min(14, absences_30 * 4)
    score -= min(10, mandatory_overdue * 5)
    score += min(8, completed_trainings * 2)
    score += min(4, active_projects)
    if employee.status != "actif":
        score -= 12
    return max(35, min(96, round(score)))


def employee_risk_payload(employee: Employee, as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    engagement = employee_engagement_score(employee, as_of=as_of)
    overdue_tasks = sum(
        1 for task in employee.tasks
        if task.due_date and task.due_date < as_of and task.status != "Terminé"
    )
    absences_30 = sum(
        1 for attendance in employee.attendances
        if attendance.date and attendance.date >= as_of - timedelta(days=30) and (attendance.status or "").lower() == "absent"
    )
    mandatory_overdue = sum(
        1 for enrollment in employee.training_enrollments
        if enrollment.mandatory and enrollment.due_date and enrollment.due_date < as_of and enrollment.status != "completed"
    )
    training_completed = sum(1 for enrollment in employee.training_enrollments if enrollment.status == "completed")
    active_projects = max(1, sum(1 for assignment in employee.project_assignments if assignment.is_active))

    factors = [
        {"label": "Charge de travail", "value": min(95, 24 + overdue_tasks * 18 + active_projects * 4)},
        {"label": "Assiduité", "value": min(95, 18 + absences_30 * 17)},
        {"label": "Formation obligatoire", "value": min(95, 15 + mandatory_overdue * 22)},
        {"label": "Engagement déclaré", "value": min(95, max(10, 100 - engagement))},
        {"label": "Reconnaissance / progression", "value": min(95, 28 + max(0, 3 - training_completed) * 9)},
    ]
    top_factors = sorted(factors, key=lambda item: item["value"], reverse=True)[:3]
    score = round(sum(item["value"] for item in top_factors) / len(top_factors))
    level = "red" if score >= 70 else "orange" if score >= 45 else "green"
    recommendation = {
        "Charge de travail": "Rééquilibrer la charge, clarifier les priorités et revoir les échéances des projets actifs.",
        "Assiduité": "Prévoir un point de suivi et analyser les causes des absences récentes avec le manager.",
        "Formation obligatoire": "Débloquer rapidement les formations obligatoires et lever les freins d'accès.",
        "Engagement déclaré": "Planifier un échange de proximité et mettre en place un plan d'accompagnement ciblé.",
        "Reconnaissance / progression": "Proposer un feedback structuré, une perspective d'évolution et un plan de développement.",
    }.get(top_factors[0]["label"], "Prévoir un entretien ciblé avec le collaborateur.")

    return {
        "employee_id": employee.id,
        "employee_name": f"{employee.first_name} {employee.last_name}",
        "department": employee.department.name if employee.department else "Non assigné",
        "title": employee.job.title if employee.job else "Collaborateur",
        "tenure": employee_tenure_label(employee),
        "score": float(score),
        "level": level,
        "recommendation": recommendation,
        "factors": top_factors,
        "computed_at": datetime.now(timezone.utc),
        "engagement": engagement,
    }


def department_engagement(department_employees: Iterable[Employee]) -> int:
    employees = list(department_employees)
    if not employees:
        return 0
    return round(sum(employee_engagement_score(employee) for employee in employees) / len(employees))


def next_benefits_enrollment_label(today: date | None = None, employee: Employee | None = None) -> str:
    today = today or date.today()
    if employee and getattr(employee, "benefit_enrollments", None):
        dated = [benefit.renewal_date for benefit in employee.benefit_enrollments if benefit.renewal_date and benefit.renewal_date >= today]
        if dated:
            return min(dated).strftime("%d %B %Y")
    next_windows = [date(today.year, 7, 1), date(today.year, 10, 1)]
    upcoming = next((window for window in next_windows if window >= today), date(today.year + 1, 1, 15))
    return upcoming.strftime("%d %B %Y")


def benefits_status_for_employee(employee: Employee) -> str:
    active_benefits = [benefit for benefit in getattr(employee, "benefit_enrollments", []) if benefit.status in {"active", "eligible", "enrolled"}]
    if active_benefits:
        if any(benefit.renewal_date and benefit.renewal_date < date.today() for benefit in active_benefits):
            return "Renouvellement requis"
        if any((benefit.tier_label or "").lower().startswith("premium") for benefit in active_benefits):
            return "Premium"
        return "Active"
    has_active_contract = any(contract.is_active for contract in employee.contracts)
    if employee.status != "actif" or not has_active_contract:
        return "À régulariser"
    if any(enrollment.mandatory and enrollment.status != "completed" for enrollment in employee.training_enrollments):
        return "Vérification en cours"
    return "Active"


def interviews_to_schedule(team: list[Employee], interviews: list[Interview], today: datetime | None = None) -> int:
    today = today or datetime.now(timezone.utc)
    next_by_employee: dict[str, Interview] = {}
    for interview in interviews:
        current = next_by_employee.get(interview.employee_id)
        if current is None or interview.scheduled_at > current.scheduled_at:
            next_by_employee[interview.employee_id] = interview

    count = 0
    for employee in team:
        latest = next_by_employee.get(employee.id)
        if latest is None:
            count += 1
            continue
        if latest.status == "À planifier":
            count += 1
            continue
        if latest.scheduled_at < today or latest.scheduled_at > today + timedelta(days=45):
            count += 1
    return count


def build_turnover_projection(monthly_scores: list[int], headcount: int) -> list[dict]:
    projections = []
    for index, score in enumerate(monthly_scores, start=1):
        projected_departures = max(1, round((score / 100) * max(headcount, 12) * 0.06))
        confidence = max(0.62, min(0.93, 0.9 - index * 0.03 + (12 - min(score, 12)) * 0.002))
        target_date = date.today().replace(day=1) + timedelta(days=32 * index)
        projections.append(
            {
                "month": target_date.strftime("%Y-%m"),
                "projected_departures": projected_departures,
                "confidence": round(confidence, 2),
            }
        )
    return projections


def build_interview_index(interviews: list[Interview]) -> dict[str, list[Interview]]:
    index: dict[str, list[Interview]] = defaultdict(list)
    for interview in interviews:
        index[interview.employee_id].append(interview)
    return index
