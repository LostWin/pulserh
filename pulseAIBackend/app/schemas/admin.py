from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GuardrailCreate(BaseModel):
    name: str
    pattern: str
    action: str  # "block", "warn", "redact"
    description: Optional[str] = None
    is_active: bool = True
    priority: int = 0

class GuardrailUpdate(BaseModel):
    name: Optional[str] = None
    pattern: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

class GuardrailResponse(BaseModel):
    id: str
    name: str
    pattern: str
    action: str
    description: Optional[str] = None
    is_active: bool
    priority: int
    triggered_count: int = 0
    created_by: Optional[str] = None
    created_at: datetime

class GuardrailTestRequest(BaseModel):
    text: str
    pattern: Optional[str] = None  # Si fourni, teste ce pattern spécifique

class AIConfig(BaseModel):
    provider: str = "openrouter"
    model_name: str = "mistralai/mistral-7b-instruct"
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = ""
    guardrails_enabled: bool = True

class AIConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    guardrails_enabled: Optional[bool] = None
