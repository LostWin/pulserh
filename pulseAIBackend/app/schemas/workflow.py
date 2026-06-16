from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import date, datetime

class OnboardingRequest(BaseModel):
    employee_id: str

class OffboardingRequest(BaseModel):
    employee_id: str
    departure_date: date
    reason: str

class StepResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    step_type: str = "automated"
    status: Literal["pending", "running", "done", "failed"]
    due_date: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    urgency: str = "medium"
    priority: int = 3
    sequence: int = 0
    rationale: Optional[str] = None
    external_ticket_id: Optional[str] = None

    class Config:
        from_attributes = True

class WorkflowResponse(BaseModel):
    id: str
    type: str # ex: "onboarding", "offboarding"
    employee_id: str
    employee_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    status: Literal["generating", "draft", "running", "completed", "failed"]
    progress_percent: int
    created_at: Optional[datetime] = None
    steps: List[StepResponse]

    class Config:
        from_attributes = True

class WorkflowApproveRequest(BaseModel):
    steps: List[StepResponse]
