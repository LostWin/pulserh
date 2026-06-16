from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import DataAccessPolicy, Employee


ROLE_PRIORITY = ["admin", "director", "hr", "manager", "collaborator"]
SUPPORTED_ROLES = ["collaborator", "manager", "hr", "director", "admin"]
EMPLOYEE_RESOURCE_FIELDS = {
    "self": [
        "id",
        "first_name",
        "last_name",
        "email",
        "department",
        "status",
        "contract_type",
        "manager_id",
        "salary",
        "phone",
        "hire_date",
        "manager_name",
        "leave_balance",
        "job_title",
        "performance_score",
        "focus_objective_title",
        "focus_objective_progress_pct",
        "benefits_status",
        "mobility_status",
        "primary_benefit_label",
        "career_focus_title",
        "readiness_level",
        "mobility_target",
        "promotion_last_title",
        "promotion_effective_date_label",
        "tenure_label",
    ],
    "detail": [
        "id",
        "first_name",
        "last_name",
        "email",
        "department",
        "status",
        "contract_type",
        "manager_id",
        "salary",
        "phone",
        "hire_date",
        "manager_name",
        "leave_balance",
        "job_title",
        "performance_score",
        "focus_objective_title",
        "focus_objective_progress_pct",
        "benefits_status",
        "mobility_status",
        "primary_benefit_label",
        "career_focus_title",
        "readiness_level",
        "mobility_target",
        "promotion_last_title",
        "promotion_effective_date_label",
        "tenure_label",
    ],
    "list": [
        "id",
        "first_name",
        "last_name",
        "email",
        "department",
        "status",
        "contract_type",
        "manager_id",
        "job_title",
        "performance_score",
        "focus_objective_title",
        "focus_objective_progress_pct",
        "benefits_status",
        "mobility_status",
        "primary_benefit_label",
        "career_focus_title",
        "readiness_level",
        "mobility_target",
        "promotion_last_title",
        "promotion_effective_date_label",
        "manager_name",
        "tenure_label",
    ],
}
DOCUMENT_RESOURCE_FIELDS = {
    "list": [
        "name",
        "type",
        "size",
        "file_path",
        "uploaded_by",
        "created_at",
        "allowed_roles",
        "rag_enabled",
        "rag_status",
        "rag_last_synced_at",
        "rag_error",
    ],
    "viewer": [
        "name",
        "can_preview",
        "allowed_roles",
        "rag_enabled",
        "rag_status",
        "rag_last_synced_at",
        "rag_error",
    ],
}
LEAVE_RESOURCE_FIELDS = {
    "request": [
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "reason",
    ],
    "suggestion": [
        "message",
        "primary_action",
        "secondary_action",
    ],
}
PREDICTION_RESOURCE_FIELDS = {
    "risk": [
        "employee_name",
        "department",
        "title",
        "tenure",
        "score",
        "level",
        "recommendation",
        "factors",
    ],
    "turnover": [
        "months",
        "summary",
    ],
    "simulation": [
        "impact_description",
        "projected_turnover_change",
    ],
}
CAREER_RESOURCE_FIELDS = {
    "detail": [
        "rationale",
        "mentor_name",
        "next_step",
        "target_job_title",
        "target_department",
        "notes",
    ],
}


@dataclass(frozen=True)
class EffectivePolicy:
    resource: str
    scope: str
    field_key: str
    role: str
    visibility: str
    mask_type: str | None = None
    conditions_json: dict[str, Any] | None = None
    description: str | None = None
    source: str = "default"
    policy_id: str | None = None
    updated_by: str | None = None


DEFAULT_POLICIES: list[EffectivePolicy] = [
    EffectivePolicy("employee", "self", "salary", "collaborator", "visible"),
    EffectivePolicy("employee", "self", "phone", "collaborator", "visible"),
    EffectivePolicy("employee", "self", "leave_balance", "collaborator", "visible"),
    EffectivePolicy("employee", "self", "email", "collaborator", "visible"),
    EffectivePolicy("employee", "detail", "salary", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "phone", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "email", "collaborator", "visible"),
    EffectivePolicy("employee", "detail", "leave_balance", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "performance_score", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "focus_objective_title", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "focus_objective_progress_pct", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "benefits_status", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "primary_benefit_label", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "mobility_status", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "mobility_target", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "career_focus_title", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "readiness_level", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "promotion_last_title", "collaborator", "hidden"),
    EffectivePolicy("employee", "detail", "promotion_effective_date_label", "collaborator", "hidden"),

    EffectivePolicy("employee", "detail", "salary", "manager", "hidden"),
    EffectivePolicy("employee", "detail", "salary", "hr", "visible"),
    EffectivePolicy("employee", "detail", "salary", "admin", "visible"),
    EffectivePolicy("employee", "detail", "phone", "manager", "masked", "phone"),
    EffectivePolicy("employee", "detail", "phone", "hr", "visible"),
    EffectivePolicy("employee", "detail", "phone", "admin", "visible"),
    EffectivePolicy("employee", "detail", "leave_balance", "manager", "visible"),
    EffectivePolicy("employee", "detail", "leave_balance", "hr", "visible"),
    EffectivePolicy("employee", "detail", "leave_balance", "admin", "visible"),
    EffectivePolicy("employee", "detail", "email", "manager", "visible"),
    EffectivePolicy("employee", "detail", "email", "hr", "visible"),
    EffectivePolicy("employee", "detail", "email", "admin", "visible"),
    EffectivePolicy("employee", "detail", "performance_score", "manager", "visible"),
    EffectivePolicy("employee", "detail", "focus_objective_title", "manager", "visible"),
    EffectivePolicy("employee", "detail", "focus_objective_progress_pct", "manager", "visible"),
    EffectivePolicy("employee", "detail", "benefits_status", "manager", "masked", "full"),
    EffectivePolicy("employee", "detail", "primary_benefit_label", "manager", "masked", "full"),
    EffectivePolicy("employee", "detail", "mobility_status", "manager", "visible"),
    EffectivePolicy("employee", "detail", "mobility_target", "manager", "visible"),
    EffectivePolicy("employee", "detail", "career_focus_title", "manager", "visible"),
    EffectivePolicy("employee", "detail", "readiness_level", "manager", "visible"),
    EffectivePolicy("employee", "detail", "promotion_last_title", "manager", "visible"),
    EffectivePolicy("employee", "detail", "promotion_effective_date_label", "manager", "visible"),
    EffectivePolicy("employee", "detail", "performance_score", "hr", "visible"),
    EffectivePolicy("employee", "detail", "focus_objective_title", "hr", "visible"),
    EffectivePolicy("employee", "detail", "focus_objective_progress_pct", "hr", "visible"),
    EffectivePolicy("employee", "detail", "benefits_status", "hr", "visible"),
    EffectivePolicy("employee", "detail", "mobility_status", "hr", "visible"),
    EffectivePolicy("employee", "detail", "performance_score", "admin", "visible"),
    EffectivePolicy("employee", "detail", "focus_objective_title", "admin", "visible"),
    EffectivePolicy("employee", "detail", "focus_objective_progress_pct", "admin", "visible"),
    EffectivePolicy("employee", "detail", "benefits_status", "admin", "visible"),
    EffectivePolicy("employee", "detail", "primary_benefit_label", "admin", "visible"),
    EffectivePolicy("employee", "detail", "mobility_status", "admin", "visible"),
    EffectivePolicy("employee", "detail", "mobility_target", "admin", "visible"),
    EffectivePolicy("employee", "detail", "career_focus_title", "admin", "visible"),
    EffectivePolicy("employee", "detail", "readiness_level", "admin", "visible"),
    EffectivePolicy("employee", "detail", "promotion_last_title", "admin", "visible"),
    EffectivePolicy("employee", "detail", "promotion_effective_date_label", "admin", "visible"),
    EffectivePolicy("employee", "list", "email", "hr", "visible"),
    EffectivePolicy("employee", "list", "email", "admin", "visible"),
    EffectivePolicy("employee", "list", "performance_score", "hr", "visible"),
    EffectivePolicy("employee", "list", "focus_objective_title", "hr", "visible"),
    EffectivePolicy("employee", "list", "focus_objective_progress_pct", "hr", "visible"),
    EffectivePolicy("employee", "list", "benefits_status", "hr", "visible"),
    EffectivePolicy("employee", "list", "mobility_status", "hr", "visible"),
    EffectivePolicy("employee", "list", "performance_score", "admin", "visible"),
    EffectivePolicy("employee", "list", "focus_objective_title", "admin", "visible"),
    EffectivePolicy("employee", "list", "focus_objective_progress_pct", "admin", "visible"),
    EffectivePolicy("employee", "list", "benefits_status", "admin", "visible"),
    EffectivePolicy("employee", "list", "primary_benefit_label", "admin", "visible"),
    EffectivePolicy("employee", "list", "mobility_status", "admin", "visible"),
    EffectivePolicy("employee", "list", "mobility_target", "admin", "visible"),
    EffectivePolicy("employee", "list", "career_focus_title", "admin", "visible"),
    EffectivePolicy("employee", "list", "readiness_level", "admin", "visible"),
    EffectivePolicy("employee", "list", "promotion_last_title", "admin", "visible"),
    EffectivePolicy("employee", "list", "promotion_effective_date_label", "admin", "visible"),
    EffectivePolicy("document", "list", "uploaded_by", "collaborator", "hidden"),
    EffectivePolicy("document", "list", "uploaded_by", "manager", "masked", "email"),
    EffectivePolicy("document", "list", "uploaded_by", "director", "masked", "email"),
    EffectivePolicy("document", "list", "uploaded_by", "hr", "visible"),
    EffectivePolicy("document", "list", "uploaded_by", "admin", "visible"),
    EffectivePolicy("document", "list", "allowed_roles", "collaborator", "hidden"),
    EffectivePolicy("document", "list", "allowed_roles", "manager", "hidden"),
    EffectivePolicy("document", "list", "allowed_roles", "director", "hidden"),
    EffectivePolicy("document", "list", "allowed_roles", "hr", "visible"),
    EffectivePolicy("document", "list", "allowed_roles", "admin", "visible"),
    EffectivePolicy("document", "list", "rag_enabled", "collaborator", "hidden"),
    EffectivePolicy("document", "list", "rag_status", "collaborator", "hidden"),
    EffectivePolicy("document", "list", "rag_error", "collaborator", "hidden"),
    EffectivePolicy("document", "viewer", "allowed_roles", "collaborator", "hidden"),
    EffectivePolicy("document", "viewer", "allowed_roles", "manager", "hidden"),
    EffectivePolicy("document", "viewer", "allowed_roles", "director", "hidden"),
    EffectivePolicy("document", "viewer", "rag_enabled", "collaborator", "hidden"),
    EffectivePolicy("document", "viewer", "rag_status", "collaborator", "hidden"),
    EffectivePolicy("document", "viewer", "rag_error", "collaborator", "hidden"),
    EffectivePolicy("leave", "request", "reason", "collaborator", "visible"),
    EffectivePolicy("leave", "suggestion", "message", "collaborator", "visible"),
    EffectivePolicy("prediction", "risk", "score", "manager", "visible"),
    EffectivePolicy("prediction", "risk", "recommendation", "manager", "visible"),
    EffectivePolicy("prediction", "risk", "factors", "manager", "visible"),
    EffectivePolicy("prediction", "risk", "score", "hr", "visible"),
    EffectivePolicy("prediction", "risk", "recommendation", "hr", "visible"),
    EffectivePolicy("prediction", "risk", "factors", "hr", "visible"),
    EffectivePolicy("prediction", "risk", "recommendation", "director", "hidden"),
    EffectivePolicy("prediction", "risk", "factors", "director", "hidden"),
    EffectivePolicy("career", "detail", "rationale", "collaborator", "hidden"),
    EffectivePolicy("career", "detail", "mentor_name", "collaborator", "hidden"),
    EffectivePolicy("career", "detail", "next_step", "collaborator", "hidden"),
    EffectivePolicy("career", "detail", "target_job_title", "collaborator", "hidden"),
    EffectivePolicy("career", "detail", "target_department", "collaborator", "hidden"),
    EffectivePolicy("career", "detail", "notes", "collaborator", "hidden"),
    EffectivePolicy("career", "detail", "rationale", "manager", "visible", conditions_json={"manager_of_target": True}),
    EffectivePolicy("career", "detail", "mentor_name", "manager", "visible", conditions_json={"manager_of_target": True}),
    EffectivePolicy("career", "detail", "next_step", "manager", "visible", conditions_json={"manager_of_target": True}),
    EffectivePolicy("career", "detail", "target_job_title", "manager", "visible", conditions_json={"manager_of_target": True}),
    EffectivePolicy("career", "detail", "target_department", "manager", "visible", conditions_json={"manager_of_target": True}),
    EffectivePolicy("career", "detail", "notes", "manager", "visible", conditions_json={"manager_of_target": True}),
    EffectivePolicy("career", "detail", "rationale", "hr", "visible"),
    EffectivePolicy("career", "detail", "mentor_name", "hr", "visible"),
    EffectivePolicy("career", "detail", "next_step", "hr", "visible"),
    EffectivePolicy("career", "detail", "target_job_title", "hr", "visible"),
    EffectivePolicy("career", "detail", "target_department", "hr", "visible"),
    EffectivePolicy("career", "detail", "notes", "hr", "visible"),
    EffectivePolicy("career", "detail", "rationale", "admin", "visible"),
    EffectivePolicy("career", "detail", "mentor_name", "admin", "visible"),
    EffectivePolicy("career", "detail", "next_step", "admin", "visible"),
    EffectivePolicy("career", "detail", "target_job_title", "admin", "visible"),
    EffectivePolicy("career", "detail", "target_department", "admin", "visible"),
    EffectivePolicy("career", "detail", "notes", "admin", "visible"),
]


def get_primary_role(roles: list[str]) -> str:
    for role in ROLE_PRIORITY:
        if role in roles:
            return role
    return "collaborator"


def get_resource_catalog() -> list[dict[str, Any]]:
    resources = {
        "employee": EMPLOYEE_RESOURCE_FIELDS,
        "document": DOCUMENT_RESOURCE_FIELDS,
        "leave": LEAVE_RESOURCE_FIELDS,
        "prediction": PREDICTION_RESOURCE_FIELDS,
        "career": CAREER_RESOURCE_FIELDS,
    }
    return [
        {
            "resource": resource,
            "scopes": list(scopes.keys()),
            "fields": sorted({field for fields in scopes.values() for field in fields}),
            "roles": SUPPORTED_ROLES,
        }
        for resource, scopes in resources.items()
    ]


async def get_effective_policies(
    db: AsyncSession | None,
    resource: str,
    scope: str,
) -> list[EffectivePolicy]:
    defaults = {
        (item.resource, item.scope, item.field_key, item.role): item
        for item in DEFAULT_POLICIES
        if item.resource == resource and item.scope == scope
    }
    rows = []
    if db is not None:
        rows = (
            await db.execute(
                select(DataAccessPolicy).where(
                    DataAccessPolicy.resource == resource,
                    DataAccessPolicy.scope == scope,
                )
            )
        ).scalars().all()
    for row in rows:
        defaults[(row.resource, row.scope, row.field_key, row.role)] = EffectivePolicy(
            resource=row.resource,
            scope=row.scope,
            field_key=row.field_key,
            role=row.role,
            visibility=row.visibility,
            mask_type=row.mask_type,
            conditions_json=row.conditions_json,
            description=row.description,
            source="custom",
            policy_id=row.id,
            updated_by=row.updated_by,
        )
    return sorted(defaults.values(), key=lambda item: (item.field_key, item.role))


async def apply_field_access(
    db: AsyncSession | None,
    *,
    resource: str,
    scope: str,
    payload: dict[str, Any],
    role: str,
    context: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    policy_map = {
        item.field_key: item
        for item in await get_effective_policies(db, resource, scope)
        if item.role == role
    }
    context = context or {}
    filtered = dict(payload)
    field_visibility: dict[str, str] = {}
    for field_key, value in payload.items():
        policy = policy_map.get(field_key)
        if policy is None:
            field_visibility[field_key] = "visible"
            continue
        visibility = resolve_visibility(policy, context)
        filtered[field_key] = apply_visibility(value, visibility, policy.mask_type)
        field_visibility[field_key] = visibility
    return filtered, field_visibility


def resolve_visibility(policy: EffectivePolicy, context: dict[str, Any]) -> str:
    conditions = policy.conditions_json or {}
    if not conditions:
        return policy.visibility
    if conditions.get("self_only") and not context.get("is_self"):
        return "hidden"
    if conditions.get("manager_of_target") and not context.get("is_manager_of_target"):
        return "hidden"
    return policy.visibility


def apply_visibility(value: Any, visibility: str, mask_type: str | None) -> Any:
    if visibility in {"visible", "readonly"}:
        return value
    if visibility == "hidden":
        return None
    return mask_value(value, mask_type)


def mask_value(value: Any, mask_type: str | None) -> Any:
    if value is None:
        return None
    if mask_type == "email" and isinstance(value, str) and "@" in value:
        local, domain = value.split("@", 1)
        if len(local) <= 2:
            return f"{local[0]}***@{domain}"
        return f"{local[:2]}***@{domain}"
    if mask_type == "phone" and isinstance(value, str):
        digits = value[-2:] if len(value) >= 2 else value
        return f"*** *** {digits}"
    if isinstance(value, str):
        return "••••"
    return None


def build_employee_access_context(current_employee: Employee | None, target_employee: Employee) -> dict[str, Any]:
    return {
        "is_self": bool(current_employee and current_employee.id == target_employee.id),
        "is_manager_of_target": bool(current_employee and target_employee.manager_id == current_employee.id),
        "same_department": bool(
            current_employee
            and current_employee.department_id
            and target_employee.department_id
            and current_employee.department_id == target_employee.department_id
        ),
    }
