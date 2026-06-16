from datetime import datetime
from typing import Any, Dict, List, Literal
from pydantic import BaseModel


class RiskScoreResponse(BaseModel):
    employee_id: str
    score: float
    level: Literal["green", "orange", "red"]
    computed_at: datetime


class RiskDetailsResponse(BaseModel):
    employee_id: str
    score: float
    level: Literal["green", "orange", "red"]
    features: Dict[str, Any]
    computed_at: datetime


class RiskActionsResponse(BaseModel):
    employee_id: str
    level: Literal["green", "orange", "red"]
    actions: List[str]


class MonthProjection(BaseModel):
    month: str  # format "YYYY-MM"
    projected_departures: int
    confidence: float


class TurnoverProjectionResponse(BaseModel):
    months: List[MonthProjection]


class SimulationRequest(BaseModel):
    employee_id: str
    scenario_type: str           # ex: "salary_increase", "reduce_overdue"
    parameters: Dict[str, Any]   # ex: {"salary_increase_pct": 5}


class SimulationResponse(BaseModel):
    original_score: float
    simulated_score: float
    projected_turnover_change: float  # delta en pourcentage
    impact_description: str
