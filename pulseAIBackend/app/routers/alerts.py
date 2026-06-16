import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.alert import AlertResponse, ActionPlanRequest, AlertStateResponse, AlertSyncResponse
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_any_role, require_admin
from app.services.alerting_service import alerting_service
from app.core.security import verify_token
from app.services.websocket_manager import websocket_manager

router = APIRouter(prefix="/alerts", tags=["Alerts"])
logger = logging.getLogger(__name__)

# Dépendances RBAC communes
alert_read_roles = require_any_role("manager", "hr", "admin", "director")
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


def current_user_from_token(token: str) -> CurrentUser:
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token does not contain user ID")

    realm_access = payload.get("realm_access", {})
    roles = realm_access.get("roles", [])
    return CurrentUser(
        id=user_id,
        email=payload.get("email", ""),
        roles=roles,
        department=payload.get("department"),
    )

# Routes "security" placées AVANT "/{id}" pour éviter le shadowing

@router.get("/security", response_model=List[AlertResponse], dependencies=[Depends(require_admin)])
async def get_security_alerts(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Alertes de sécurité (guardrails IA, accès illégitimes)"""
    alerts = await alerting_service.list_alerts_for_user(
        current_user=current_user,
        filters={"type": "security"},
        db=db,
    )
    return alerts

@router.post("/security/{id}/block-user", dependencies=[Depends(require_admin)])
def block_user_from_alert(id: str):
    """Bloquer temporairement un utilisateur lié à l'alerte de sécurité"""
    logger.warning(f"Admin a bloqué l'utilisateur suite à l'alerte de sécurité {id}")
    return {"status": "User blocked", "alert_id": id}


@router.websocket("/ws")
async def alerts_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return

    try:
        current_user = current_user_from_token(token)
    except Exception as error:
        logger.warning("WebSocket auth failed: %s", error)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    await websocket_manager.connect(websocket, current_user.id, current_user.roles)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception:
        websocket_manager.disconnect(websocket)
        raise

@router.post("/sync", response_model=AlertSyncResponse, dependencies=[Depends(require_any_role("hr", "admin", "director"))])
async def sync_alerts(db: AsyncSession = Depends(get_db)):
    return await alerting_service.sync_alerts(db)


@router.get("", response_model=List[AlertResponse], dependencies=[Depends(alert_read_roles)])
async def list_alerts(
    filters: AlertFilters = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste des alertes (filtrables)"""
    return await alerting_service.list_alerts_for_user(
        current_user=current_user,
        filters={
            "severity": filters.severity,
            "status": filters.status,
            "employee_id": filters.employee_id,
            "type": filters.type,
        },
        db=db,
    )

@router.get("/{id}", response_model=AlertResponse, dependencies=[Depends(alert_read_roles)])
async def get_alert(id: str, current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Détail d'une alerte"""
    alert = await alerting_service.get_alert_for_user(id, current_user, db=db)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    return alert

@router.post("/{id}/read", response_model=AlertStateResponse, dependencies=[Depends(alert_read_roles)])
async def read_alert(id: str, current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await alerting_service.mark_as_read(id, current_user.id, db=db)

@router.post("/{id}/archive", response_model=AlertStateResponse, dependencies=[Depends(alert_read_roles)])
async def archive_alert(id: str, current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await alerting_service.archive_alert(id, current_user.id, db=db)

@router.post("/{id}/resolve", dependencies=[Depends(alert_action_roles)])
async def resolve_alert(id: str, current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Marquer une alerte comme traitée"""
    return await alerting_service.resolve_alert(id, current_user.email, db=db)

@router.post("/{id}/action", dependencies=[Depends(alert_action_roles)])
async def set_action_plan(id: str, plan: ActionPlanRequest, db: AsyncSession = Depends(get_db)):
    """Associer un plan d'action (rétention, suivi, etc.)"""
    return await alerting_service.set_action_plan(id, plan.description, db=db)
