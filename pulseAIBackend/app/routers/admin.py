"""
Router Admin — Console d'administration (Guardrails, Config IA, Logs).

Les guardrails et la configuration IA sont persistés en base de données.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.schemas.admin import (
    GuardrailCreate, GuardrailUpdate, GuardrailResponse,
    GuardrailTestRequest, AIConfig, AIConfigUpdate
)
from app.core.rbac import require_admin
from app.models.domain import Guardrail, AIConfiguration
from app.database import get_db
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.services.guardrail_service import guardrail_service
from app.services.llm_client import llm_client

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)

# Dépendance commune : Tous les endpoints sont restreints au rôle "admin"
admin_only = require_admin


# ═══════════════════════════════════════════════════════════════
# Configuration IA
# ═══════════════════════════════════════════════════════════════

@router.get("/ai/config", response_model=AIConfig, dependencies=[Depends(admin_only)])
async def get_ai_config(db: AsyncSession = Depends(get_db)):
    """Configuration LLM globale depuis la base de données."""
    logger.info("GET /admin/ai/config")
    result = await db.execute(select(AIConfiguration).limit(1))
    config = result.scalar_one_or_none()
    
    if not config:
        # Créer la config par défaut si elle n'existe pas
        config = AIConfiguration()
        db.add(config)
        await db.commit()
        await db.refresh(config)
    
    return AIConfig(
        provider=config.provider,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        system_prompt=config.system_prompt or "",
        guardrails_enabled=config.guardrails_enabled,
    )


@router.put("/ai/config", response_model=AIConfig, dependencies=[Depends(admin_only)])
async def update_ai_config(
    config_update: AIConfigUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Modifier la configuration LLM et recharger le client dynamiquement."""
    logger.info(f"PUT /admin/ai/config | user={current_user.email}, update={config_update.model_dump(exclude_none=True)}")
    
    result = await db.execute(select(AIConfiguration).limit(1))
    config = result.scalar_one_or_none()
    
    if not config:
        config = AIConfiguration()
        db.add(config)
        await db.flush()
    
    # Appliquer les modifications
    update_data = config_update.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    config.updated_by = current_user.email
    
    await db.commit()
    await db.refresh(config)
    
    # Reconfigurer le LLMClient dynamiquement
    if "provider" in update_data or "model_name" in update_data:
        try:
            llm_client.reconfigure(
                provider=config.provider,
                model=config.model_name,
            )
            logger.info(f"LLMClient reconfiguré : provider={config.provider}, model={config.model_name}")
        except Exception as e:
            logger.error(f"Erreur lors de la reconfiguration du LLMClient : {e}")
    
    return AIConfig(
        provider=config.provider,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        system_prompt=config.system_prompt or "",
        guardrails_enabled=config.guardrails_enabled,
    )


# ═══════════════════════════════════════════════════════════════
# Guardrails CRUD
# ═══════════════════════════════════════════════════════════════

@router.get("/guardrails", response_model=List[GuardrailResponse], dependencies=[Depends(admin_only)])
async def list_guardrails(db: AsyncSession = Depends(get_db)):
    """Liste des guardrails depuis la base de données."""
    logger.info("GET /admin/guardrails")
    result = await db.execute(
        select(Guardrail).order_by(Guardrail.priority.desc(), Guardrail.created_at.desc())
    )
    guardrails = result.scalars().all()
    
    return [
        GuardrailResponse(
            id=g.id,
            name=g.name,
            pattern=g.pattern,
            action=g.action,
            description=g.description,
            is_active=g.is_active,
            priority=g.priority,
            triggered_count=g.triggered_count,
            created_by=g.created_by,
            created_at=g.created_at,
        )
        for g in guardrails
    ]


@router.post("/guardrails", response_model=GuardrailResponse, dependencies=[Depends(admin_only)])
async def create_guardrail(
    guardrail: GuardrailCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ajouter une règle de filtrage IA."""
    logger.info(f"POST /admin/guardrails | name={guardrail.name}, user={current_user.email}")
    
    new_guardrail = Guardrail(
        name=guardrail.name,
        pattern=guardrail.pattern,
        action=guardrail.action,
        description=guardrail.description,
        is_active=guardrail.is_active,
        priority=guardrail.priority,
        created_by=current_user.email,
    )
    db.add(new_guardrail)
    await db.commit()
    await db.refresh(new_guardrail)
    
    return GuardrailResponse(
        id=new_guardrail.id,
        name=new_guardrail.name,
        pattern=new_guardrail.pattern,
        action=new_guardrail.action,
        description=new_guardrail.description,
        is_active=new_guardrail.is_active,
        priority=new_guardrail.priority,
        triggered_count=new_guardrail.triggered_count,
        created_by=new_guardrail.created_by,
        created_at=new_guardrail.created_at,
    )


@router.put("/guardrails/{guardrail_id}", response_model=GuardrailResponse, dependencies=[Depends(admin_only)])
async def update_guardrail(
    guardrail_id: str,
    guardrail_update: GuardrailUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Modifier un guardrail existant."""
    logger.info(f"PUT /admin/guardrails/{guardrail_id}")
    
    result = await db.execute(select(Guardrail).filter(Guardrail.id == guardrail_id))
    guardrail = result.scalar_one_or_none()
    
    if not guardrail:
        raise HTTPException(status_code=404, detail="Guardrail introuvable")
    
    update_data = guardrail_update.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(guardrail, key, value)
    
    await db.commit()
    await db.refresh(guardrail)
    
    return GuardrailResponse(
        id=guardrail.id,
        name=guardrail.name,
        pattern=guardrail.pattern,
        action=guardrail.action,
        description=guardrail.description,
        is_active=guardrail.is_active,
        priority=guardrail.priority,
        triggered_count=guardrail.triggered_count,
        created_by=guardrail.created_by,
        created_at=guardrail.created_at,
    )


@router.delete("/guardrails/{guardrail_id}", dependencies=[Depends(admin_only)])
async def delete_guardrail(guardrail_id: str, db: AsyncSession = Depends(get_db)):
    """Supprimer un guardrail."""
    logger.info(f"DELETE /admin/guardrails/{guardrail_id}")
    
    result = await db.execute(select(Guardrail).filter(Guardrail.id == guardrail_id))
    guardrail = result.scalar_one_or_none()
    
    if not guardrail:
        raise HTTPException(status_code=404, detail="Guardrail introuvable")
    
    await db.delete(guardrail)
    await db.commit()
    return {"message": "Guardrail supprimé", "id": guardrail_id}


@router.post("/guardrails/test", dependencies=[Depends(admin_only)])
async def test_guardrail(request: GuardrailTestRequest, db: AsyncSession = Depends(get_db)):
    """Tester les guardrails sur un texte donné."""
    logger.info(f"POST /admin/guardrails/test | text_len={len(request.text)}")
    
    if request.pattern:
        # Tester un pattern spécifique
        result = guardrail_service.test_pattern(request.pattern, request.text)
        return {"status": "Test completed", **result}
    else:
        # Tester contre tous les guardrails actifs
        check = await guardrail_service.check_input(request.text, db)
        return {
            "status": "Test completed",
            "passed": check.passed,
            "action": check.action,
            "message": check.message,
            "triggered_rules": check.triggered_rules,
        }


# ═══════════════════════════════════════════════════════════════
# Autres endpoints admin (conservés)
# ═══════════════════════════════════════════════════════════════

@router.get("/logs", dependencies=[Depends(admin_only)])
def get_ai_logs():
    """Logs d'interaction IA (anonymisés)"""
    return []

@router.get("/logs/security", dependencies=[Depends(admin_only)])
def get_security_logs():
    """Logs d'authentification et appels API"""
    return []

@router.get("/users", dependencies=[Depends(admin_only)])
def get_users():
    """Liste des utilisateurs (Keycloak)"""
    return []

@router.post("/users/{id}/block", dependencies=[Depends(admin_only)])
def block_user(id: str):
    """Bloquer un utilisateur dans le SI"""
    logger.warning(f"Admin blocked user {id}")
    return {"status": "User blocked", "id": id}

@router.post("/users/{id}/unblock", dependencies=[Depends(admin_only)])
def unblock_user(id: str):
    """Débloquer un utilisateur"""
    logger.info(f"Admin unblocked user {id}")
    return {"status": "User unblocked", "id": id}

@router.post("/ai/documents", dependencies=[Depends(admin_only)])
def upload_ai_document(file: UploadFile = File(...)):
    """Uploader un document directement dans la base vectorielle (Qdrant)"""
    return {"status": "Document uploaded and vectorized", "filename": file.filename}

@router.get("/metrics/ai", dependencies=[Depends(admin_only)])
def get_ai_metrics():
    """Métriques d'usage de l'assistant (coûts, latence, requêtes)"""
    return {"total_requests": 1500, "avg_response_time_ms": 350, "token_cost_usd": 12.5}

@router.get("/audit", dependencies=[Depends(admin_only)])
def get_audit_logs():
    """Logs d'audit génériques (imports, modifications employés, etc.)"""
    return []