from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

class DepartmentImport(BaseModel):
    id: str
    name: str
    manager_id: Optional[str] = None

class JobImport(BaseModel):
    id: str
    title: str
    level: Optional[str] = None
    description: Optional[str] = None

class EmployeeImport(BaseModel):
    id: str
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    hire_date: date
    status: str
    department_id: Optional[str] = None
    job_id: Optional[str] = None
    manager_id: Optional[str] = None

class ContractImport(BaseModel):
    id: str
    employee_id: str
    contract_type: str
    start_date: date
    end_date: Optional[date] = None
    salary: float
    is_active: bool

class LeaveImport(BaseModel):
    id: str
    employee_id: str
    start_date: date
    end_date: date
    leave_type: str
    status: str
    reason: Optional[str] = None

class ProjectImport(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: str

class TaskImport(BaseModel):
    id: str
    project_id: str
    assignee_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    due_date: Optional[date] = None
    evaluation_score: Optional[float] = None

class AttendanceImport(BaseModel):
    id: str
    employee_id: str
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str

class ImportHistoryResponse(BaseModel):
    id: str
    filename: str
    entity_type: str
    author_name: Optional[str] = None
    processed_lines: int
    created_lines: int
    updated_lines: int
    error_count: int
    status: str
    full_report: Optional[dict] = None
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True
