from pydantic import BaseModel
from typing import Optional, Literal, Any
from datetime import datetime

class AlertResponse(BaseModel):
    id: str
    type: str
    severity: Literal["low", "medium", "critical"]
    title: str
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    workflow_id: Optional[str] = None
    department: Optional[str] = None
    message: str
    link: Optional[str] = None
    source: str = "pulse_ai"
    created_at: datetime
    status: Literal["open", "in_progress", "resolved"]
    is_read: bool = False
    is_archived: bool = False
    action_plan: Optional[str] = None
    payload: Optional[dict[str, Any]] = None

class ActionPlanRequest(BaseModel):
    description: str


class AlertListFilters(BaseModel):
    severity: Optional[Literal["low", "medium", "critical"]] = None
    status: Optional[Literal["open", "in_progress", "resolved"]] = None
    employee_id: Optional[str] = None
    type: Optional[str] = None


class AlertStateResponse(BaseModel):
    status: str
    id: str


class AlertSyncResponse(BaseModel):
    created: int
    updated: int
