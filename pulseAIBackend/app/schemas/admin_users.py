from pydantic import BaseModel
from typing import List, Optional


class AdminUserItem(BaseModel):
    id: str
    username: str
    name: str
    email: str
    role: str
    active: bool
    lastLogin: str
    mfa: bool
    employee_id: Optional[str] = None


class AdminUsersResponse(BaseModel):
    items: List[AdminUserItem]
