from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class LeaveBalanceItem(BaseModel):
    id: str
    label: str
    value: float
    unit: str
    tag: str
    tag_color: str


class LeaveCalendarEvent(BaseModel):
    date: str
    label: str
    color: str
    text: str


class LeaveActivityItem(BaseModel):
    id: str
    title: str
    sub: str
    color: str


class LeaveRequestItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    leave_type: str
    start_date: str
    end_date: str
    status: str
    reason: Optional[str] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")


class LeaveAISuggestion(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    primary_action: str
    secondary_action: str
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")


class LeaveOverviewResponse(BaseModel):
    balances: List[LeaveBalanceItem]
    calendar_events: List[LeaveCalendarEvent]
    activity: List[LeaveActivityItem]
    requests: List[LeaveRequestItem]
    ai_suggestion: LeaveAISuggestion


class LeaveRequestCreate(BaseModel):
    leave_type: str
    start_date: str
    end_date: str
    reason: Optional[str] = None
