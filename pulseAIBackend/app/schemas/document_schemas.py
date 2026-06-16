from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import datetime

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    type: str
    size: str
    file_path: Optional[str] = None
    uploaded_by: Optional[str] = None
    status: Optional[str] = "validated"
    employee_id: Optional[str] = None
    document_type_id: Optional[str] = None
    created_at: datetime
    allowed_roles: Optional[List[str]] = []
    rag_enabled: Optional[bool] = False
    rag_status: Optional[str] = "disabled"
    rag_last_synced_at: Optional[datetime] = None
    rag_error: Optional[str] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")

class DocumentAccessEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_email: str
    action: str
    roles: List[str] = []
    details: Optional[dict[str, Any]] = None
    created_at: datetime
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")

class DocumentSettingsUpdate(BaseModel):
    allowed_roles: List[str]
    rag_enabled: bool

class DocumentViewerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    can_preview: bool
    allowed_roles: Optional[List[str]] = None
    rag_enabled: Optional[bool] = None
    rag_status: Optional[str] = None
    rag_last_synced_at: Optional[datetime] = None
    rag_error: Optional[str] = None
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility")
