from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

class DepartmentImport(BaseModel):
    id: str
    name: str
    manager_id: Optional[str] = None

class JobImport(BaseModel):
    id: str
    title: str
    level: Optional[str] = None
    description: Optional[str] = None

class EmployeeImport(BaseModel):
    id: str
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    hire_date: date
    status: str
    department_id: Optional[str] = None
    job_id: Optional[str] = None
    manager_id: Optional[str] = None

class ContractImport(BaseModel):
    id: str
    employee_id: str
    contract_type: str
    start_date: date
    end_date: Optional[date] = None
    salary: float
    is_active: bool

class LeaveImport(BaseModel):
    id: str
    employee_id: str
    start_date: date
    end_date: date
    leave_type: str
    status: str
    reason: Optional[str] = None

class ProjectImport(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: str
    priority: Optional[str] = None
    business_domain: Optional[str] = None
    required_skill_ids: Optional[str] = None
    manager_id: Optional[str] = None

class TaskImport(BaseModel):
    id: str
    project_id: str
    assignee_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    due_date: Optional[date] = None
    evaluation_score: Optional[float] = None

class AttendanceImport(BaseModel):
    id: str
    employee_id: str
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str

class SkillImport(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    level_scale: Optional[str] = None
    is_certifiable: bool = False
    is_active: bool = True

class EmployeeSkillImport(BaseModel):
    id: str
    employee_id: str
    skill_id: str
    proficiency_level: str
    years_experience: Optional[float] = None
    is_primary: bool = False
    last_assessed_at: Optional[datetime] = None
    source: Optional[str] = None
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    confidence_score: Optional[float] = None

class TrainingCourseImport(BaseModel):
    id: str
    title: str
    provider: Optional[str] = None
    duration_hours: Optional[float] = None
    level: Optional[str] = None
    format: Optional[str] = None
    description: Optional[str] = None
    target_skill_id: Optional[str] = None
    required_for_job_family: Optional[str] = None
    difficulty: Optional[str] = None
    delivery_mode: Optional[str] = None
    mandatory_for_roles: Optional[str] = None

class TrainingEnrollmentImport(BaseModel):
    id: str
    employee_id: str
    training_id: str
    status: str
    assigned_at: Optional[datetime] = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    mandatory: bool = False
    assigned_by: Optional[str] = None
    recommendation_reason: Optional[str] = None

class ProjectAssignmentImport(BaseModel):
    id: str
    project_id: str
    employee_id: str
    role_on_project: Optional[str] = None
    allocation_pct: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True

class EngagementSnapshotImport(BaseModel):
    id: str
    employee_id: str
    score: int = Field(ge=0, le=100)
    source: str
    pulse_label: Optional[str] = None
    comment: Optional[str] = None
    trend: Optional[int] = None
    risk_band: Optional[str] = None
    source_signals: Optional[str] = None
    captured_at: Optional[datetime] = None

class PerformanceReviewImport(BaseModel):
    id: str
    employee_id: str
    review_period: str
    reviewer_name: Optional[str] = None
    overall_score: Optional[float] = None
    strengths: Optional[str] = None
    improvement_areas: Optional[str] = None
    summary: Optional[str] = None
    reviewed_at: Optional[datetime] = None

class PerformanceObjectiveImport(BaseModel):
    id: str
    employee_id: str
    title: str
    description: Optional[str] = None
    status: str
    progress_pct: int = Field(ge=0, le=100)
    due_date: Optional[date] = None
    created_at: Optional[datetime] = None

class BenefitPlanImport(BaseModel):
    id: str
    name: str
    provider: Optional[str] = None
    category: str
    coverage_summary: Optional[str] = None
    enrollment_month: Optional[int] = None
    is_active: bool = True

class EmployeeBenefitImport(BaseModel):
    id: str
    employee_id: str
    benefit_plan_id: str
    status: str
    effective_date: Optional[date] = None
    renewal_date: Optional[date] = None
    tier_label: Optional[str] = None
    employer_contribution: Optional[float] = None
    notes: Optional[str] = None

class CareerPathImport(BaseModel):
    id: str
    employee_id: str
    target_job_id: Optional[str] = None
    target_title: str
    readiness_level: str
    next_step: Optional[str] = None
    mentor_name: Optional[str] = None
    last_reviewed_at: Optional[datetime] = None

class MobilityRequestImport(BaseModel):
    id: str
    employee_id: str
    target_department_id: Optional[str] = None
    target_job_id: Optional[str] = None
    request_type: str
    status: str
    rationale: Optional[str] = None
    requested_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

class PromotionHistoryImport(BaseModel):
    id: str
    employee_id: str
    previous_job_title: Optional[str] = None
    new_job_title: str
    effective_date: date
    notes: Optional[str] = None

class ImportHistoryResponse(BaseModel):
    id: str
    filename: str
    entity_type: str
    author_name: Optional[str] = None
    processed_lines: int
    created_lines: int
    updated_lines: int
    error_count: int
    status: str
    full_report: Optional[dict] = None
    created_at: Optional[datetime] = None
    user_id: str

    class Config:
        from_attributes = True
