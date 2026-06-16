from pydantic import BaseModel, Field
from typing import Optional


class BenefitEnrollmentResponse(BaseModel):
    id: str
    plan_name: str
    category: str
    provider: Optional[str] = None
    status: str
    tier_label: Optional[str] = None
    effective_date_label: Optional[str] = None
    renewal_date_label: Optional[str] = None
    employer_contribution: Optional[float] = None
    coverage_summary: Optional[str] = None


class CareerPathResponse(BaseModel):
    id: str
    target_title: str
    readiness_level: str
    next_step: Optional[str] = None
    mentor_name: Optional[str] = None
    last_reviewed_at_label: Optional[str] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")


class MobilityRequestResponse(BaseModel):
    id: str
    request_type: str
    status: str
    target_department: Optional[str] = None
    target_job_title: Optional[str] = None
    rationale: Optional[str] = None
    requested_at_label: Optional[str] = None
    reviewed_at_label: Optional[str] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")


class PromotionHistoryResponse(BaseModel):
    id: str
    previous_job_title: Optional[str] = None
    new_job_title: str
    effective_date_label: str
    notes: Optional[str] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")


class EmployeeCareerOverviewResponse(BaseModel):
    career_paths: list[CareerPathResponse]
    mobility_requests: list[MobilityRequestResponse]
    promotions: list[PromotionHistoryResponse]


class MobilityRequestCreate(BaseModel):
    target_department: Optional[str] = None
    target_job_title: Optional[str] = None
    request_type: str = "internal_move"
    rationale: Optional[str] = None


class EmployeeProgramOverviewItem(BaseModel):
    employee_id: str
    employee_name: str
    department: Optional[str] = None
    job_title: Optional[str] = None
    benefits_status: Optional[str] = None
    primary_benefit_label: Optional[str] = None
    career_focus_title: Optional[str] = None
    readiness_level: Optional[str] = None
    mobility_status: Optional[str] = None
    mobility_target: Optional[str] = None
    promotion_last_title: Optional[str] = None
    promotion_effective_date_label: Optional[str] = None
    manager_name: Optional[str] = None
    tenure_label: Optional[str] = None
    next_career_review_label: Optional[str] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")


class EmployeeProgramOverviewResponse(BaseModel):
    items: list[EmployeeProgramOverviewItem]
    total: int
    page: int = 1
    page_size: int = 20
    active_benefits_count: int
    mobility_open_count: int
    ready_now_count: int


class EmployeeProgramsFiltersResponse(BaseModel):
    departments: list[str]
    readiness_levels: list[str]
    benefits_statuses: list[str]
    mobility_statuses: list[str]
