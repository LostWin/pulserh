from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: str
    name: str
    type: str
    size: str
    file_path: str
    uploaded_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
