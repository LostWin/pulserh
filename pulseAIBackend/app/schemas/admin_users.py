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


class AdminUserCreate(BaseModel):
    employee_id: str
    role: str
    password: Optional[str] = None
    send_email: bool = False

class AdminUnlinkedEmployee(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    department: Optional[str] = None
    job: Optional[str] = None
    user_id: Optional[str] = None

class AdminUnlinkedEmployeesResponse(BaseModel):
    items: List[AdminUnlinkedEmployee]
