from pydantic import BaseModel, Field
from typing import Optional, List


class InterviewItem(BaseModel):
    id: str
    collaborator_id: str
    collaborator: str
    date: str
    time: str
    status: str
    title: str
    interview_type: str = "one_on_one"
    location: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None
    summary: Optional[str] = None
    next_actions: List[str] = []


class InterviewCreate(BaseModel):
    employee_id: str
    scheduled_at: str
    title: str = Field(default="Entretien individuel")
    interview_type: str = Field(default="one_on_one")
    location: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: Optional[int] = 45


class InterviewUpdate(BaseModel):
    scheduled_at: Optional[str] = None
    title: Optional[str] = None
    interview_type: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None
    summary: Optional[str] = None
    next_actions: Optional[List[str]] = None


class InterviewOverview(BaseModel):
    items: List[InterviewItem]
    planned_count: int
    pending_count: int
    average_duration_minutes: int
