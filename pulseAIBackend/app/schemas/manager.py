from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class ObjectiveCreate(BaseModel):
    employee_id: str = Field(..., description="ID du collaborateur")
    title: str = Field(..., description="Titre de l'objectif")
    description: Optional[str] = Field(None, description="Description détaillée de l'objectif")
    target_date: Optional[date] = Field(None, description="Date d'échéance cible")

class ObjectiveUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, description="planned, in_progress, completed, cancelled")
    progress_pct: Optional[int] = Field(None, ge=0, le=100, description="Pourcentage d'avancement")
    target_date: Optional[date] = None

class ObjectiveResponse(BaseModel):
    id: str
    employee_id: str
    owner_id: Optional[str]
    title: str
    description: Optional[str]
    status: str
    progress_pct: int
    target_date: Optional[date]
    created_at: datetime
    updated_at: datetime

class AutoScheduleRequest(BaseModel):
    employee_id: str = Field(..., description="ID du collaborateur pour lequel planifier l'entretien")
    interview_type: str = Field(default="one_on_one", description="Type d'entretien")
    title: Optional[str] = Field(default="Point de suivi (1:1)", description="Titre de l'entretien")
    duration_minutes: Optional[int] = Field(default=30, description="Durée estimée en minutes")

class TeamVibeResponse(BaseModel):
    team_size: int
    avg_engagement: int
    at_risk_count: int
    overall_vibe_score: int
    summary_message: str
    recommended_actions: List[str]
