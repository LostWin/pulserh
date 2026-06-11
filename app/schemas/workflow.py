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
    status: Literal["pending", "running", "done", "failed"]
    executed_at: Optional[datetime] = None

class WorkflowResponse(BaseModel):
    id: str
    type: str # ex: "onboarding", "offboarding"
    employee_id: str
    status: str
    progress_percent: int
    steps: List[StepResponse]