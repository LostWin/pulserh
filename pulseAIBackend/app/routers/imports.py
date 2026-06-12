from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.import_service import process_csv_import
from app.dependencies import get_current_user

# Models
from app.models.domain import Department, Job, Employee, Contract, Leave, Project, Task, Attendance

# Schemas
from app.schemas.import_schemas import (
    DepartmentImport, JobImport, EmployeeImport, ContractImport, 
    LeaveImport, ProjectImport, TaskImport, AttendanceImport, ImportHistoryResponse
)
from app.schemas.employee import ImportReport

router = APIRouter(
    prefix="/imports",
    tags=["Imports"]
)

@router.get("/history", response_model=list[ImportHistoryResponse])
async def get_import_history(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from sqlalchemy import select
    from app.models.domain import ImportHistory
    result = await db.execute(select(ImportHistory).order_by(ImportHistory.created_at.desc()))
    return result.scalars().all()

@router.post("/departments", response_model=ImportReport)
async def import_departments(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, DepartmentImport, Department, current_user.id, current_user.email, "departments")

@router.post("/jobs", response_model=ImportReport)
async def import_jobs(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, JobImport, Job, current_user.id, current_user.email, "jobs")

@router.post("/employees", response_model=ImportReport)
async def import_employees(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, EmployeeImport, Employee, current_user.id, current_user.email, "employees")

@router.post("/contracts", response_model=ImportReport)
async def import_contracts(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, ContractImport, Contract, current_user.id, current_user.email, "contracts")

@router.post("/leaves", response_model=ImportReport)
async def import_leaves(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, LeaveImport, Leave, current_user.id, current_user.email, "leaves")

@router.post("/projects", response_model=ImportReport)
async def import_projects(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, ProjectImport, Project, current_user.id, current_user.email, "projects")

@router.post("/tasks", response_model=ImportReport)
async def import_tasks(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, TaskImport, Task, current_user.id, current_user.email, "tasks")

@router.post("/attendances", response_model=ImportReport)
async def import_attendances(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, AttendanceImport, Attendance, current_user.id, current_user.email, "attendances")
