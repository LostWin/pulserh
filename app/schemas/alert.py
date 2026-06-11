from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class AlertResponse(BaseModel):
    id: str
    type: str # ex: "disengagement", "security", "workflow_failed"
    severity: Literal["low", "medium", "critical"]
    employee_id: Optional[str] = None
    message: str
    created_at: datetime
    status: Literal["open", "resolved"]
    action_plan: Optional[str] = None

class ActionPlanRequest(BaseModel):
    description: str