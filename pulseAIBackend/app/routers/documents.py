import logging
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.document import (
    DocumentGenerateRequest, DocumentResponse, 
    BatchGenerateRequest, BatchGenerateResponse
)
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_hr, require_any_role

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger(__name__)

# Groupes de rôles pour la simplification
doc_generate_roles = require_any_role("collaborator", "manager", "hr")
collab_hr_roles = require_any_role("collaborator", "hr")

@router.post("/generate", response_model=DocumentResponse, dependencies=[Depends(doc_generate_roles)])
def generate_document(request: DocumentGenerateRequest, current_user: CurrentUser = Depends(get_current_user)):
    """Générer un document RH individuel"""
    # Si le user est un simple collaborateur, il ne peut générer que ses propres documents
    if "hr" not in current_user.roles and "manager" not in current_user.roles:
        if request.employee_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Vous ne pouvez générer des documents que pour vous-même."
            )
            
    # Stub: Appel au service de génération LLM/Template
    # doc_url = document_generator.create(request.type, request.custom_fields)
    
    return DocumentResponse(
        id=str(uuid.uuid4()),
        type=request.type,
        employee_id=request.employee_id,
        url="https://minio.local/documents/dummy-doc.pdf",
        created_at=datetime.now(timezone.utc),
        format=request.format
    )

@router.post("/generate/batch", response_model=BatchGenerateResponse, dependencies=[Depends(require_hr)])
def generate_documents_batch(request: BatchGenerateRequest):
    """Génération batch pour un département (Processus Asynchrone)"""
    # Stub: Envoi de la tâche dans une queue (ex: Celery)
    job_id = f"job-{uuid.uuid4()}"
    return BatchGenerateResponse(job_id=job_id, status="pending")

@router.get("/", response_model=List[DocumentResponse], dependencies=[Depends(collab_hr_roles)])
def list_documents(current_user: CurrentUser = Depends(get_current_user)):
    """Liste des documents générés (les siens ou tous si RH)"""
    # Si RH: liste complète. Sinon: where employee_id == current_user.id
    return []

@router.get("/templates", dependencies=[Depends(require_hr)])
def list_templates():
    """Liste des modèles disponibles (Administration RH)"""
    return [{"id": "tpl-1", "name": "Modèle Attestation"}]

@router.put("/templates/{id}", dependencies=[Depends(require_hr)])
def update_template(id: str):
    """Modifier un modèle"""
    return {"status": "Template updated", "id": id}

@router.get("/{id}/download", dependencies=[Depends(collab_hr_roles)])
def download_document(id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Télécharger un document (Lien présigné MinIO)"""
    # Stub: Vérifier que le document appartient bien à l'employé (sauf si RH)
    # url = minio_client.presigned_get_object(...)
    return {"status": "Downloading", "id": id, "url": f"https://minio.local/documents/{id}.pdf"}