from pydantic import BaseModel, ConfigDict, Field
from typing import List, Literal, Dict, Any, Optional
from datetime import datetime

class RiskScoreResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str
    employee_name: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    tenure: Optional[str] = None
    score: float
    level: Literal["green", "orange", "red"]
    recommendation: Optional[str] = None
    factors: Optional[List[Dict[str, Any]]] = None
    computed_at: datetime
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")

class MonthProjection(BaseModel):
    month: str # Format attendu : "YYYY-MM"
    projected_departures: int
    confidence: float # De 0.0 à 1.0

class TurnoverProjectionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    months: List[MonthProjection]
    summary: Optional[str] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")

class SimulationRequest(BaseModel):
    scenario_type: str
    parameters: Dict[str, Any]

class SimulationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    impact_description: str
    projected_turnover_change: float # ex: -2.5 pour signifier une baisse de 2.5% du turnover
    engagement: Optional[float] = None
    engagement_gain: Optional[float] = None
    turnover: Optional[float] = None
    savings: Optional[float] = None
    cost: Optional[float] = None
    net: Optional[float] = None
    roi: Optional[float] = None
    projection: Optional[List[Dict[str, Any]]] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")
