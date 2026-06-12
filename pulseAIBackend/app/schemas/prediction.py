from pydantic import BaseModel
from typing import List, Literal, Dict, Any
from datetime import datetime

class RiskScoreResponse(BaseModel):
    employee_id: str
    score: float
    level: Literal["green", "orange", "red"]
    computed_at: datetime

class MonthProjection(BaseModel):
    month: str # Format attendu : "YYYY-MM"
    projected_departures: int
    confidence: float # De 0.0 à 1.0

class TurnoverProjectionResponse(BaseModel):
    months: List[MonthProjection]

class SimulationRequest(BaseModel):
    scenario_type: str
    parameters: Dict[str, Any]

class SimulationResponse(BaseModel):
    impact_description: str
    projected_turnover_change: float # ex: -2.5 pour signifier une baisse de 2.5% du turnover