from typing import Any, Literal

from pydantic import BaseModel, Field


Visibility = Literal["visible", "masked", "hidden", "readonly"]
MaskType = Literal["full", "email", "phone"]


class DataAccessPolicyBase(BaseModel):
    resource: str = Field(..., description="Ressource métier ciblée", examples=["employee"])
    scope: str = Field(..., description="Contexte de restitution", examples=["detail"])
    field_key: str = Field(..., description="Champ concerné", examples=["salary"])
    role: str = Field(..., description="Rôle applicatif", examples=["manager"])
    visibility: Visibility = Field(..., description="Niveau de visibilité à appliquer")
    mask_type: MaskType | None = Field(None, description="Type de masquage si visibility=masked")
    conditions_json: dict[str, Any] | None = Field(None, description="Conditions métier complémentaires")
    description: str | None = Field(None, description="Description administrateur")


class DataAccessPolicyCreate(DataAccessPolicyBase):
    pass


class DataAccessPolicyUpdate(BaseModel):
    visibility: Visibility | None = None
    mask_type: MaskType | None = None
    conditions_json: dict[str, Any] | None = None
    description: str | None = None


class DataAccessPolicyResponse(DataAccessPolicyBase):
    id: str
    updated_by: str | None = None
    source: Literal["default", "custom"] = "custom"


class DataAccessPreviewRequest(BaseModel):
    resource: str
    scope: str
    role: str
    payload: dict[str, Any]
    context: dict[str, Any] | None = None


class DataAccessPreviewResponse(BaseModel):
    payload: dict[str, Any]
    field_visibility: dict[str, str]


class DataAccessResourceResponse(BaseModel):
    resource: str
    scopes: list[str]
    fields: list[str]
    roles: list[str]
