from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SkillCatalogItem(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    level_scale: Optional[str] = None
    is_certifiable: bool = False
    is_active: bool = True

    class Config:
        from_attributes = True


class EmployeeSkillItem(BaseModel):
    id: str
    employee_id: str
    skill_id: str
    skill_name: str
    category: Optional[str] = None
    proficiency_level: str
    years_experience: Optional[float] = None
    is_primary: bool = False
    source: Optional[str] = None
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    last_assessed_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    confidence_score: Optional[float] = None


class EmployeeSkillCreate(BaseModel):
    skill_id: str
    proficiency_level: str = "intermediate"
    years_experience: Optional[float] = None
    is_primary: bool = False
    source: Optional[str] = None
    last_assessed_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=100)


class EmployeeSkillUpdate(BaseModel):
    proficiency_level: Optional[str] = None
    years_experience: Optional[float] = None
    is_primary: Optional[bool] = None
    source: Optional[str] = None
    last_assessed_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=100)


class ValidateSkillPayload(BaseModel):
    validated_by: Optional[str] = None


class TrainingCatalogItem(BaseModel):
    id: str
    title: str
    provider: Optional[str] = None
    duration_hours: Optional[float] = None
    level: Optional[str] = None
    format: Optional[str] = None
    description: Optional[str] = None
    target_skill_id: Optional[str] = None
    target_skill_name: Optional[str] = None
    required_for_job_family: Optional[str] = None
    difficulty: Optional[str] = None
    delivery_mode: Optional[str] = None
    mandatory_for_roles: List[str] = []


class TrainingEnrollmentItem(BaseModel):
    id: str
    employee_id: str
    training_id: str
    title: str
    provider: Optional[str] = None
    status: str
    mandatory: bool = False
    assigned_at: Optional[datetime] = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    assigned_by: Optional[str] = None
    recommendation_reason: Optional[str] = None


class AssignTrainingPayload(BaseModel):
    training_id: str
    due_date: Optional[date] = None
    mandatory: bool = False
    recommendation_reason: Optional[str] = None


class CompleteTrainingPayload(BaseModel):
    employee_id: str
    score: Optional[float] = Field(None, ge=0, le=100)


class TrainingRecommendationItem(BaseModel):
    training_id: str
    title: str
    provider: Optional[str] = None
    target_skill_name: Optional[str] = None
    relevance_score: int
    reasons: List[str]
    mandatory: bool = False


class ProjectItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: str
    priority: Optional[str] = None
    business_domain: Optional[str] = None
    required_skill_ids: List[str] = []
    required_skill_names: List[str] = []
    manager_id: Optional[str] = None
    manager_name: Optional[str] = None


class EmployeeProjectAssignmentItem(BaseModel):
    id: str
    project_id: str
    project_name: str
    status: str
    priority: Optional[str] = None
    business_domain: Optional[str] = None
    role_on_project: Optional[str] = None
    allocation_pct: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    required_skill_names: List[str] = []
