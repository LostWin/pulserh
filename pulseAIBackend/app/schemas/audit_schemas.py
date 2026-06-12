from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditLogResponse(BaseModel):
    id: str
    user_email: str
    action: str
    log_type: str
    ip_address: Optional[str] = None
    critical: bool
    timestamp: datetime

    class Config:
        from_attributes = True
