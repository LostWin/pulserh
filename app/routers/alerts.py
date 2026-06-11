import logging
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query

from app.schemas.alert import AlertResponse, ActionPlanRequest
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_any_role, require_admin

router = APIRouter(prefix="/alerts", tags=["Alerts"])
logger = logging.getLogger(__name__)

# Dépendances RBAC communes
alert_read_roles = require_any_role("manager", "hr", "admin")
alert_action_roles = require_any_role("manager", "hr")

class AlertFilters:
    def __init__(
        self,
        severity: Optional[str] = Query(None, description="low, medium, critical"),
        status: Optional[str] = Query(None, description="open, resolved"),
        employee_id: Optional[str] = Query(None),
        type: Optional[str] = Query(None)
    ):
        self.severity = severity
        self.status = status
        self.employee_id = employee_id
        self.type = type

# Routes "security" placées AVANT "/{id}" pour éviter le shadowing

@router.get("/security", response_model=List[AlertResponse], dependencies=[Depends(require_admin)])
def get_security_alerts():
    """Alertes de sécurité (guardrails IA, accès illégitimes)"""
    return []

@router.post("/security/{id}/block-user", dependencies=[Depends(require_admin)])
def block_user_from_alert(id: str):
    """Bloquer temporairement un utilisateur lié à l'alerte de sécurité"""
    logger.warning(f"Admin a bloqué l'utilisateur suite à l'alerte de sécurité {id}")
    return {"status": "User blocked", "alert_id": id}

@router.get("/", response_model=List[AlertResponse], dependencies=[Depends(alert_read_roles)])
def list_alerts(filters: AlertFilters = Depends(), current_user: CurrentUser = Depends(get_current_user)):
    """Liste des alertes (filtrables)"""
    # Stub: Si le rôle est uniquement "manager", on filtrera les alertes
    # pour ne remonter que celles concernant son équipe.
    return []

@router.get("/{id}", response_model=AlertResponse, dependencies=[Depends(alert_read_roles)])
def get_alert(id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Détail d'une alerte"""
    return AlertResponse(
        id=id,
        type="disengagement",
        severity="critical",
        message="Risque élevé de départ détecté (score > 85%)",
        created_at=datetime.now(timezone.utc),
        status="open"
    )

@router.post("/{id}/resolve", dependencies=[Depends(alert_action_roles)])
def resolve_alert(id: str):
    """Marquer une alerte comme traitée"""
    return {"status": "Resolved", "id": id}

@router.post("/{id}/action", dependencies=[Depends(alert_action_roles)])
def set_action_plan(id: str, plan: ActionPlanRequest):
    """Associer un plan d'action (rétention, suivi, etc.)"""
    return {"status": "Action plan associated", "id": id, "plan": plan.description}