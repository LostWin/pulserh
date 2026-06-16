from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EngagementSnapshotItem(BaseModel):
    id: str
    score: int
    source: str
    pulse_label: Optional[str] = None
    comment: Optional[str] = None
    trend: Optional[int] = None
    risk_band: Optional[str] = None
    source_signals: Optional[dict] = None
    captured_at: datetime


class EngagementEventItem(BaseModel):
    id: str
    event_type: str
    label: str
    intensity: int
    source: str
    payload: Optional[dict] = None
    occurred_at: datetime


class EmployeeEngagementResponse(BaseModel):
    employee_id: str
    current_score: int
    trend_label: str
    risk_band: str
    snapshots: List[EngagementSnapshotItem]
    events: List[EngagementEventItem]


class PerformanceReviewItem(BaseModel):
    id: str
    review_type: str
    period_label: str
    score: float
    summary: Optional[str] = None
    strengths: List[str] = []
    improvement_areas: List[str] = []
    reviewer_name: Optional[str] = None
    created_at: datetime


class PerformanceObjectiveItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str
    progress_pct: int
    target_date: Optional[date] = None
    owner_name: Optional[str] = None


class EmployeePerformanceResponse(BaseModel):
    employee_id: str
    current_score: float
    latest_review: Optional[PerformanceReviewItem] = None
    reviews: List[PerformanceReviewItem]
    objectives: List[PerformanceObjectiveItem]


class ObjectiveCreatePayload(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "planned"
    progress_pct: int = Field(0, ge=0, le=100)
    target_date: Optional[date] = None


class InterviewSummaryPayload(BaseModel):
    outcome: Optional[str] = None
    summary: Optional[str] = None
    next_actions: List[str] = []
