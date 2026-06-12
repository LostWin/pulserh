import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.domain import Department, Employee

from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.schemas.employee import EmployeeResponse
from app.core.rbac import require_hr, require_any_role

router = APIRouter(prefix="/departments", tags=["Departments"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[DepartmentResponse], dependencies=[Depends(require_any_role("hr", "manager", "director"))])
async def list_departments(db: AsyncSession = Depends(get_db)):
    """Liste de tous les départements"""
    # Fetch departments
    query = select(Department)
    result = await db.execute(query)
    departments_db = result.scalars().all()
    
    # We also need employee counts and manager emails. 
    # For simplicity, we just fetch all employees.
    emp_query = select(Employee)
    emp_result = await db.execute(emp_query)
    all_employees = emp_result.scalars().all()
    
    emp_map = {emp.id: emp for emp in all_employees}
    
    dept_counts = {}
    for emp in all_employees:
        if emp.department_id:
            dept_counts[emp.department_id] = dept_counts.get(emp.department_id, 0) + 1
            
    items = []
    for dept in departments_db:
        manager_name = None
        if dept.manager_id and dept.manager_id in emp_map:
            emp = emp_map[dept.manager_id]
            manager_name = f"{emp.first_name} {emp.last_name}"
            
        items.append(
            DepartmentResponse(
                id=dept.id,
                name=dept.name,
                employee_count=dept_counts.get(dept.id, 0),
                manager=manager_name
            )
        )
    return items

@router.get("/{id}", response_model=DepartmentResponse, dependencies=[Depends(require_hr)])
def get_department(id: str):
    """Détail d'un département"""
    return DepartmentResponse(id=id, name="IT", employee_count=10)

@router.post("/", response_model=DepartmentResponse, dependencies=[Depends(require_hr)])
def create_department(department: DepartmentCreate):
    """Créer un département"""
    return DepartmentResponse(id="new-id", name=department.name, manager=department.manager_email, employee_count=0)

@router.put("/{id}", response_model=DepartmentResponse, dependencies=[Depends(require_hr)])
def update_department(id: str, department: DepartmentUpdate):
    """Modifier un département (nom, manager rattaché)"""
    return DepartmentResponse(id=id, name=department.name or "Updated", manager=department.manager_email, employee_count=10)

@router.delete("/{id}", dependencies=[Depends(require_hr)])
def delete_department(id: str):
    """Supprimer un département"""
    return {"status": "Deleted", "id": id}

@router.get("/{id}/employees", response_model=List[EmployeeResponse], dependencies=[Depends(require_any_role("hr", "manager"))])
def get_department_employees(id: str):
    """Employés d'un département"""
    return []