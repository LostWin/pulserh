from pydantic import BaseModel, Field
from typing import Optional


class UserSettingsResponse(BaseModel):
    theme: str
    locale: str
    timezone: str
    digest_frequency: str
    avatar_data_url: Optional[str] = None
    profile_title: Optional[str] = None
    birth_date_label: Optional[str] = None
    address_label: Optional[str] = None
    work_location_label: Optional[str] = None
    email_enabled: bool
    in_app_enabled: bool
    slack_enabled: bool


class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    digest_frequency: Optional[str] = None
    profile_title: Optional[str] = None
    birth_date_label: Optional[str] = None
    address_label: Optional[str] = None
    work_location_label: Optional[str] = None
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    slack_enabled: Optional[bool] = None


class AvatarUploadResponse(BaseModel):
    avatar_data_url: str


class PasswordActionResponse(BaseModel):
    action: str = Field(default="UPDATE_PASSWORD")
    redirect_hint: str
