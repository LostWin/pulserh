import logging
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File

from app.schemas.admin import GuardrailCreate, GuardrailTestRequest, AIConfig
from app.core.rbac import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)

# Dépendance commune : Tous les endpoints sont restreints au rôle "admin"
admin_only = require_admin

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

@router.get("/guardrails", dependencies=[Depends(admin_only)])
def list_guardrails():
    """Règles de filtrage configurées (ex: Regex, thèmes interdits)"""
    return []

@router.post("/guardrails", dependencies=[Depends(admin_only)])
def create_guardrail(guardrail: GuardrailCreate):
    """Ajouter une règle de filtrage IA"""
    return {"status": "Guardrail created", "guardrail": guardrail.model_dump()}

@router.delete("/guardrails/{id}", dependencies=[Depends(admin_only)])
def delete_guardrail(id: str):
    """Supprimer une règle de filtrage"""
    return {"status": "Guardrail deleted", "id": id}

@router.post("/guardrails/test", dependencies=[Depends(admin_only)])
def test_guardrail(request: GuardrailTestRequest):
    """Tester un guardrail sur un texte donné"""
    # Stub: Simulation de passage dans le filtre
    is_safe = "salaire pdg" not in request.text.lower()
    return {
        "status": "Test completed", 
        "passed": is_safe, 
        "triggered_rules": [] if is_safe else ["confidential_data_rule"]
    }

@router.get("/ai/config", response_model=AIConfig, dependencies=[Depends(admin_only)])
def get_ai_config():
    """Configuration LLM globale (température, max_tokens, modèle)"""
    return AIConfig(temperature=0.7, max_tokens=2048, model_name="gpt-4o-mini")

@router.put("/ai/config", response_model=AIConfig, dependencies=[Depends(admin_only)])
def update_ai_config(config: AIConfig):
    """Modifier la configuration LLM"""
    logger.info(f"Admin updated AI config: {config.model_dump()}")
    return config

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