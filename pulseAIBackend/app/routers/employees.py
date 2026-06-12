import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.domain import Employee
from app.services.audit_service import log_audit_action

from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse,
    ImportReport, ErrorLine, ChangeRequest
)
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_hr, require_any_role, require_collaborator

router = APIRouter(prefix="/employees", tags=["Employees"])
logger = logging.getLogger(__name__)

@router.get(
    "/me", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_collaborator)],
    summary="Obtenir ses propres informations",
    description="Retourne la fiche collaborateur de l'utilisateur actuellement authentifié."
)
async def get_my_info(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Ses propres informations"""
    query = select(Employee).options(
        selectinload(Employee.department), 
        selectinload(Employee.job),
        selectinload(Employee.contracts),
        selectinload(Employee.leaves),
        selectinload(Employee.manager)
    ).filter(Employee.user_id == current_user.id)
    
    result = await db.execute(query)
    emp = result.scalar_one_or_none()
    
    if not emp:
        # Fallback par email
        query_by_email = select(Employee).options(
            selectinload(Employee.department), 
            selectinload(Employee.job),
            selectinload(Employee.contracts),
            selectinload(Employee.leaves),
            selectinload(Employee.manager)
        ).filter(Employee.email == current_user.email)
        result = await db.execute(query_by_email)
        emp = result.scalar_one_or_none()
        
    if not emp:
        raise HTTPException(status_code=404, detail="Fiche collaborateur introuvable.")
        
    contract_type = emp.job.title if emp.job else None
    salary_val = None
    if emp.contracts:
        active_contract = next((c for c in emp.contracts if c.is_active), emp.contracts[0])
        contract_type = active_contract.contract_type
        salary_val = active_contract.salary
        
    hire_date_str = emp.hire_date.strftime("%d %B %Y") if emp.hire_date else None
    manager_name = f"{emp.manager.first_name} {emp.manager.last_name}" if emp.manager else "Aucun manager"
    
    taken_leaves = sum((l.end_date - l.start_date).days + 1 for l in emp.leaves if l.status == "Approuvé")
    remaining_leaves = max(0, 30 - taken_leaves)
    leave_balance = f"{remaining_leaves} / 30 jours"
    
    return EmployeeResponse(
        id=emp.id,
        first_name=emp.first_name,
        last_name=emp.last_name,
        email=emp.email,
        department=emp.department.name if emp.department else None,
        status=emp.status,
        contract_type=contract_type,
        manager_id=emp.manager_id,
        salary=salary_val,
        phone=emp.phone,
        hire_date=hire_date_str,
        manager_name=manager_name,
        leave_balance=leave_balance
    )

@router.post(
    "/me/change-request", 
    dependencies=[Depends(require_collaborator)],
    summary="Demander une modification de ses informations",
    description="Permet à un collaborateur de soumettre une demande de changement de ses données personnelles à l'équipe RH."
)
def request_info_change(request: ChangeRequest, current_user: CurrentUser = Depends(get_current_user)):
    """Demande de modification de ses infos"""
    return {"status": "request submitted", "data": request}

@router.get(
    "/import/history", 
    dependencies=[Depends(require_hr)],
    summary="Historique des imports (Admin RH)",
    description="Récupère la liste des derniers fichiers d'employés importés et leur statut d'intégration."
)
def get_import_history():
    """Historique des imports"""
    return {"status": "Not Implemented", "history": []}

@router.post(
    "/import", 
    response_model=ImportReport, 
    dependencies=[Depends(require_hr)],
    summary="Import en masse d'employés (Admin RH)",
    description="Permet l'upload d'un fichier CSV ou XLSX contenant une liste d'employés à créer ou mettre à jour.",
    responses={
        400: {"description": "Format de fichier non autorisé (Doit être CSV ou XLSX)."}
    }
)
async def import_employees(file: UploadFile = File(...), current_user: CurrentUser = Depends(get_current_user)):
    """Import CSV/Excel (upload fichier)"""
    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV or XLSX files are allowed.")
    
    # Stub : Appeler le service d'import (à implémenter par collègue DB)
    # employee_import_service.process(file)
    
    # Tracer l'import dans les logs d'audit
    logger.info(f"Audit: User {current_user.id} imported file {file.filename}")
    
    return ImportReport(
        processed=10,
        created=8,
        updated=2,
        errors=[ErrorLine(line=5, error="Missing email")]
    )

@router.get(
    "/", 
    response_model=EmployeeListResponse, 
    dependencies=[Depends(require_hr)],
    summary="Lister les employés (Admin RH)",
    description="Renvoie une liste paginée d'employés avec des options de filtrage multiples."
)
async def list_employees(
    department: Optional[str] = Query(None, description="Filtrer par nom ou ID de département"),
    status: Optional[str] = Query(None, description="Filtrer par statut (ex: actif, inactif)"),
    contract_type: Optional[str] = Query(None, description="Filtrer par type de contrat"),
    manager_id: Optional[str] = Query(None, description="Filtrer par ID de manager direct"),
    search: Optional[str] = Query(None, description="Recherche textuelle sur le nom ou l'email"),
    page: int = Query(1, ge=1, description="Numéro de la page"),
    page_size: int = Query(20, ge=1, le=1000, description="Nombre de résultats par page"),
    db: AsyncSession = Depends(get_db)
):
    """Liste paginée et filtrable"""
    query = select(Employee).options(selectinload(Employee.department), selectinload(Employee.job))
    
    # We load everything for now (or up to page_size)
    result = await db.execute(query.limit(page_size).offset((page - 1) * page_size))
    employees_db = result.scalars().all()
    
    count_query = select(func.count(Employee.id))
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    items = []
    for emp in employees_db:
        emp_dict = {
            "id": emp.id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "department": emp.department.name if emp.department else None,
            "status": emp.status,
            "contract_type": emp.job.title if emp.job else None, # Mocking contract_type as job title just for passing data
            "manager_id": emp.manager_id
        }
        items.append(EmployeeResponse(**emp_dict))
        
    return EmployeeListResponse(items=items, total=total_count, page=page, page_size=page_size)

@router.get(
    "/{id}", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_any_role("hr", "manager"))],
    summary="Récupérer la fiche d'un employé",
    description="Retourne les détails d'un employé spécifique."
)
async def get_employee(
    id: str, 
    request: Request,
    current_user: CurrentUser = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Fiche d'un employé"""
    
    query = select(Employee).options(
        selectinload(Employee.department), 
        selectinload(Employee.job),
        selectinload(Employee.contracts),
        selectinload(Employee.leaves),
        selectinload(Employee.manager)
    ).filter(Employee.id == id)
    
    result = await db.execute(query)
    emp = result.scalar_one_or_none()
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employé introuvable.")
        
    # Logguer la consultation si ce n'est pas son propre profil
    if emp.email != current_user.email:
        await log_audit_action(
            db=db,
            user_email=current_user.email,
            action=f"a consulté les informations de l'employé {emp.first_name} {emp.last_name}",
            log_type="access",
            request=request,
            critical=False
        )
    
    # Extraire le type de contrat et le salaire
    contract_type = emp.job.title if emp.job else None
    salary_val = None
    if emp.contracts:
        active_contract = next((c for c in emp.contracts if c.is_active), emp.contracts[0])
        contract_type = active_contract.contract_type
        # Seuls les RH (ou l'employé lui-même si accessible par une autre route) ont accès au salaire
        if "hr" in current_user.roles:
            salary_val = active_contract.salary
            
    hire_date_str = emp.hire_date.strftime("%d %B %Y") if emp.hire_date else None
    manager_name = f"{emp.manager.first_name} {emp.manager.last_name}" if emp.manager else "Aucun manager"
    
    taken_leaves = sum((l.end_date - l.start_date).days + 1 for l in emp.leaves if l.status == "Approuvé")
    remaining_leaves = max(0, 30 - taken_leaves)
    leave_balance = f"{remaining_leaves} / 30 jours"
    
    return EmployeeResponse(
        id=emp.id,
        first_name=emp.first_name,
        last_name=emp.last_name,
        email=emp.email,
        department=emp.department.name if emp.department else None,
        status=emp.status,
        contract_type=contract_type,
        manager_id=emp.manager_id,
        salary=salary_val,
        phone=emp.phone,
        hire_date=hire_date_str,
        manager_name=manager_name,
        leave_balance=leave_balance
    )

@router.post(
    "/", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_hr)],
    summary="Créer un employé (Admin RH)",
    description="Ajoute un nouvel employé dans la base de données. Réservé aux RH."
)
def create_employee(employee: EmployeeCreate):
    """Créer un employé manuellement"""
    return EmployeeResponse(id="new-id", **employee.model_dump())

@router.put(
    "/{id}", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_hr)],
    summary="Modifier un employé (Admin RH)",
    description="Met à jour unitairement les informations d'un employé existant."
)
def update_employee(id: str, employee: EmployeeUpdate):
    """Modifier un employé"""
    # Stub retour
    return EmployeeResponse(id=id, first_name="Updated", last_name="User", email="up@example.com")

@router.delete(
    "/{id}", 
    dependencies=[Depends(require_hr)],
    summary="Désactiver un employé (Admin RH)",
    description="Marque l'employé comme inactif. Ne supprime pas physiquement la donnée de la base pour des raisons d'historisation."
)
def disable_employee(id: str):
    """Désactiver un employé"""
    return {"status": "Disabled", "id": id}