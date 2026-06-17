from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class MLModuleConfigResponse(BaseModel):
    module_id: str
    module_name: str
    is_enabled: bool
    mode: str  # "heuristic" | "ml"
    alert_threshold: float
    strict_mode: bool
    heuristic_params: Dict[str, Any] = {}
    ml_params: Dict[str, Any] = {}
    model_version: Optional[str] = None
    last_trained_at: Optional[datetime] = None
    training_status: str
    training_error: Optional[str] = None

    class Config:
        from_attributes = True


class MLModuleConfigUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    mode: Optional[str] = Field(None, pattern="^(heuristic|ml)$")
    alert_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    strict_mode: Optional[bool] = None
    heuristic_params: Optional[Dict[str, Any]] = None
    ml_params: Optional[Dict[str, Any]] = None
