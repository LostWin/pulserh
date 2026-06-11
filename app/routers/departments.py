import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.schemas.employee import EmployeeResponse
from app.core.rbac import require_hr, require_any_role

router = APIRouter(prefix="/departments", tags=["Departments"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[DepartmentResponse], dependencies=[Depends(require_any_role("hr", "manager", "director"))])
def list_departments():
    """Liste de tous les départements"""
    return []

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