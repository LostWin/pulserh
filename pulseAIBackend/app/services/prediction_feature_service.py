from datetime import date, timedelta
from app.models.domain import Employee
from app.services.hr_analytics_service import employee_engagement_score

def extract_employee_features(employee: Employee, as_of: date | None = None) -> dict:
    """Extrait l'ensemble des métriques brutes (features) pour alimenter le modèle de scoring."""
    as_of = as_of or date.today()
    
    engagement = employee_engagement_score(employee, as_of=as_of)
    
    overdue_tasks = sum(
        1 for task in employee.tasks
        if task.due_date and task.due_date < as_of and task.status != "Terminé"
    )
    active_projects = max(1, sum(1 for assignment in employee.project_assignments if assignment.is_active))
    
    absences_30 = sum(
        1 for attendance in employee.attendances
        if attendance.date and attendance.date >= as_of - timedelta(days=30) and (attendance.status or "").lower() == "absent"
    )
    absences_90 = sum(
        1 for attendance in employee.attendances
        if attendance.date and attendance.date >= as_of - timedelta(days=90) and (attendance.status or "").lower() == "absent"
    )
    delays_30 = sum(
        1 for attendance in employee.attendances
        if attendance.date and attendance.date >= as_of - timedelta(days=30) and (attendance.status or "").lower() == "retard"
    )

    mandatory_overdue = sum(
        1 for enrollment in employee.training_enrollments
        if enrollment.mandatory and enrollment.due_date and enrollment.due_date < as_of and enrollment.status != "completed"
    )
    training_completed = sum(1 for enrollment in employee.training_enrollments if enrollment.status == "completed")
    
    days_tenure = (as_of - employee.hire_date).days if employee.hire_date else 365

    return {
        "engagement_score": engagement,
        "overdue_tasks": overdue_tasks,
        "active_projects": active_projects,
        "absences_30": absences_30,
        "absences_90": absences_90,
        "delays_30": delays_30,
        "mandatory_training_overdue": mandatory_overdue,
        "training_completed": training_completed,
        "days_tenure": days_tenure
    }
