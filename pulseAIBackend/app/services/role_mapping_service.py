from __future__ import annotations

from app.models.domain import Employee


def infer_access_role(
    *,
    email: str | None = None,
    department_name: str | None = None,
    job_title: str | None = None,
) -> str:
    email_val = (email or "").lower()
    department_val = (department_name or "").lower()
    title_val = (job_title or "").lower()

    if any(token in email_val for token in ["admin.technique", "admin.tech@", "sysadmin"]):
        return "admin"

    if any(token in title_val for token in ["chief", "directeur général", "directrice générale", "ceo", "cpo"]):
        return "director"

    if "direction générale" in department_val or title_val.startswith("directeur") or title_val.startswith("directrice"):
        return "director"

    if any(token in department_val for token in ["ressources humaines", "human resources"]) or any(
        token in title_val for token in ["rh", "recrut", "talent", "people", "human resources"]
    ):
        return "hr"

    if any(token in title_val for token in ["manager", "lead", "responsable", "head", "supervisor"]):
        return "manager"

    return "collaborator"


def infer_access_role_for_employee(employee: Employee) -> str:
    department_name = employee.department.name if getattr(employee, "department", None) else None
    job_title = employee.job.title if getattr(employee, "job", None) else None
    return infer_access_role(
        email=employee.email,
        department_name=department_name,
        job_title=job_title,
    )
