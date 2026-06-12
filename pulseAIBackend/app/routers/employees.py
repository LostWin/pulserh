import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException

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
def get_my_info(current_user: CurrentUser = Depends(get_current_user)):
    """Ses propres informations"""
    return EmployeeResponse(
        id=current_user.id,
        first_name="Me",
        last_name="Myself",
        email=current_user.email,
        department=current_user.department,
        status="actif"
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
def list_employees(
    department: Optional[str] = Query(None, description="Filtrer par nom ou ID de département"),
    status: Optional[str] = Query(None, description="Filtrer par statut (ex: actif, inactif)"),
    contract_type: Optional[str] = Query(None, description="Filtrer par type de contrat"),
    manager_id: Optional[str] = Query(None, description="Filtrer par ID de manager direct"),
    search: Optional[str] = Query(None, description="Recherche textuelle sur le nom ou l'email"),
    page: int = Query(1, ge=1, description="Numéro de la page"),
    page_size: int = Query(20, ge=1, le=100, description="Nombre de résultats par page")
):
    """Liste paginée et filtrable"""
    return EmployeeListResponse(items=[], total=0, page=page, page_size=page_size)

@router.get(
    "/{id}", 
    response_model=EmployeeResponse, 
    dependencies=[Depends(require_any_role("hr", "manager"))],
    summary="Récupérer la fiche d'un employé",
    description="""
    Retourne les détails d'un employé spécifique. 
    
    **Règles de sécurité :**
    - Un `manager` ne peut consulter que les membres de son équipe.
    - Le champ `salary` est masqué sauf si l'utilisateur possède le rôle `hr`.
    """,
    responses={
        403: {"description": "Accès refusé. L'employé n'est pas dans votre équipe."},
        404: {"description": "Employé introuvable."}
    }
)
def get_employee(id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Fiche d'un employé"""
    
    # Règle RBAC importante : un manager ne voit que les employés de son équipe
    if "hr" not in current_user.roles:
        # Stub: Simule la vérification en DB : l'employé a-t-il manager_id == current_user.id ?
        is_in_team = True # À implémenter par l'équipe DB
        if not is_in_team:
            raise HTTPException(status_code=403, detail="Cet employé n'est pas dans votre équipe.")
            
    # Masquer le salaire si ce n'est pas un RH
    salary_val = 50000.0 if "hr" in current_user.roles else None
    
    return EmployeeResponse(
        id=id,
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        status="actif",
        salary=salary_val
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