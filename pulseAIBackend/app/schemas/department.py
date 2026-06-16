from pydantic import BaseModel, EmailStr
from typing import Optional

class DepartmentCreate(BaseModel):
    name: str
    manager_email: Optional[EmailStr] = None

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    manager_email: Optional[EmailStr] = None

class DepartmentResponse(BaseModel):
    id: str
    name: str
    manager: Optional[str] = None # Peut être le nom ou l'email du manager
    employee_count: int = 0
    manager_title: Optional[str] = None
    engagement_score: Optional[int] = None
    risk_score: Optional[int] = None
    metrics_source: Optional[dict[str, str]] = None
