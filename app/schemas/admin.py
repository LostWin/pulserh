from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GuardrailCreate(BaseModel):
    name: str
    pattern: str
    action: str # ex: "block", "alert"

class GuardrailTestRequest(BaseModel):
    text: str

class AIConfig(BaseModel):
    temperature: float
    max_tokens: int
    model_name: str
