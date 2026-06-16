from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ReportItem(BaseModel):
    id: str
    name: str
    period: str
    dept: str
    generated: str
    size: str
    format: str
    status: str


class ReportCreate(BaseModel):
    name: str
    period: str
    dept: str = "Tous"
    format: str = "PDF"


class ReportListResponse(BaseModel):
    items: List[ReportItem]
    available_departments: List[str]


class DirectionSimulationRequest(BaseModel):
    raise_pct: float = 0
    training_pct: float = 0
    remote_days: float = 0
    recognition_pct: float = 0


class DirectionSimulationResponse(BaseModel):
    engagement: float
    engagement_gain: float
    turnover: float
    savings: float
    cost: float
    net: float
    roi: Optional[float]
    projection: List[Dict[str, Any]]
