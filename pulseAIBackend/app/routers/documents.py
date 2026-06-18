import logging
import uuid
from typing import List
from pathlib import Path
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import selectinload

from app.schemas.document import (
    DocumentGenerateRequest, DocumentResponse, 
    BatchGenerateRequest, BatchGenerateResponse
)
from app.schemas.document_schemas import (
    DocumentResponse as UploadedDocumentResponse,
    DocumentAccessEventResponse,
    DocumentSettingsUpdate,
    DocumentViewerResponse,
)
from app.models.domain import Document, Employee
from app.database import get_db
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_hr, require_any_role
from app.services.document_generator import document_generator
from app.services.document_access_service import (
    ALL_DOCUMENT_ROLES,
    delete_document_from_rag,
    document_can_preview,
    guess_media_type,
    log_document_event,
    mark_document_rag_state,
    normalize_roles,
    sync_document_to_rag,
    user_can_access_document,
)
from app.services.field_access_service import apply_field_access, get_primary_role
from app.services.secure_document_storage import secure_document_storage
from app.services.audit_service import log_audit_action, log_audit

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".odt",
    ".ott",
    ".rtf",
    ".pages",
}

ALLOWED_DOCUMENT_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.text-template",
    "application/rtf",
    "text/rtf",
    "application/x-iwork-pages-sffpages",
    "application/vnd.apple.pages",
    "application/zip",
    "application/octet-stream",
}

def get_file_size_formatted(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} Ko"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} Mo"


def validate_uploaded_document(file: UploadFile) -> None:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Format non autorisé. Seuls les fichiers Word, ODT, Pages, RTF et PDF sont acceptés.",
        )

    if file.content_type and file.content_type not in ALLOWED_DOCUMENT_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Type MIME non autorisé pour ce document.",
        )

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger(__name__)

# Groupes de rôles pour la simplification
doc_generate_roles = require_any_role("collaborator", "manager", "hr")
document_access_roles = require_any_role("collaborator", "manager", "hr", "director", "admin")


async def get_document_or_404(db: AsyncSession, document_id: str) -> Document:
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.access_events))
        .filter(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return document


def ensure_document_access(document: Document, current_user: CurrentUser) -> None:
    if not user_can_access_document(document, current_user.roles, current_user.id):
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à ce document.")


async def _serialize_document(
    db: AsyncSession,
    *,
    document: Document,
    current_user: CurrentUser,
) -> UploadedDocumentResponse:
    payload = {
        "id": document.id,
        "name": document.name,
        "type": document.type,
        "size": document.size,
        "file_path": document.file_path,
        "uploaded_by": document.uploaded_by,
        "created_at": document.created_at,
        "status": document.status,
        "allowed_roles": normalize_roles(document.allowed_roles or []),
        "rag_enabled": document.rag_enabled,
        "rag_status": document.rag_status,
        "rag_last_synced_at": document.rag_last_synced_at,
        "rag_error": document.rag_error,
    }
    filtered, field_visibility = await apply_field_access(
        db,
        resource="document",
        scope="list",
        payload=payload,
        role=get_primary_role(current_user.roles),
        context={},
    )
    return UploadedDocumentResponse(**filtered, field_visibility=field_visibility)


async def _serialize_document_viewer(
    db: AsyncSession,
    *,
    document: Document,
    current_user: CurrentUser,
) -> DocumentViewerResponse:
    payload = {
        "id": document.id,
        "name": document.name,
        "can_preview": document_can_preview(document),
        "allowed_roles": normalize_roles(document.allowed_roles or []),
        "rag_enabled": document.rag_enabled,
        "rag_status": document.rag_status,
        "rag_last_synced_at": document.rag_last_synced_at,
        "rag_error": document.rag_error,
    }
    filtered, field_visibility = await apply_field_access(
        db,
        resource="document",
        scope="viewer",
        payload=payload,
        role=get_primary_role(current_user.roles),
        context={},
    )
    return DocumentViewerResponse(**filtered, field_visibility=field_visibility)

@router.post("/generate", response_model=DocumentResponse, dependencies=[Depends(doc_generate_roles)])
async def generate_document(request: DocumentGenerateRequest, current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Générer un document RH individuel"""
    logger.info(f"Requête de génération de document reçue: type={request.type}, employee_id={request.employee_id}, user={current_user.email}")
    
    if "hr" not in current_user.roles and "manager" not in current_user.roles:
        if request.employee_id != current_user.id:
            logger.error(f"Accès refusé pour {current_user.email} (tentative de génération pour {request.employee_id})")
            raise HTTPException(
                status_code=403, 
                detail="Vous ne pouvez générer des documents que pour vous-même."
            )
            
    query = select(Employee).options(selectinload(Employee.department), selectinload(Employee.job), selectinload(Employee.contracts)).filter(Employee.id == request.employee_id)
    result = await db.execute(query)
    emp = result.scalar_one_or_none()
    
    if not emp:
        logger.error(f"Employé introuvable avec l'ID {request.employee_id}")
        raise HTTPException(status_code=404, detail="Employé introuvable")

    # Préparation du contexte pour Jinja2
    salary = 0
    if emp.contracts and len(emp.contracts) > 0:
        salary = emp.contracts[0].salary
        
    context = {
        "employee": {
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "hire_date": emp.hire_date.strftime("%d/%m/%Y") if emp.hire_date else "N/A",
            "job_title": emp.job.title if emp.job else "Collaborateur",
            "department_name": emp.department.name if emp.department else "N/A"
        },
        "salary": f"{salary:,.2f}".replace(",", " "),
        "monthly_salary": f"{(salary/12):,.2f}".replace(",", " ")
    }
    
    try:
        filename, pdf_bytes = document_generator.create_pdf_bytes(
            doc_type=request.type, 
            context=context,
            custom_fields=request.custom_fields
        )
    except Exception as e:
        logger.error(f"Échec de la génération du document: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du document")

    file_size_bytes = len(pdf_bytes)
    size_str = get_file_size_formatted(file_size_bytes)
    storage_uri = secure_document_storage.upload_bytes(pdf_bytes, filename, "generated")
    
    new_doc = Document(
        name=filename,
        type=request.type,
        size=size_str,
        file_path=storage_uri,
        uploaded_by="Moteur de génération IA",
        allowed_roles=["collaborator", "hr", "admin"],
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    logger.info(f"Document enregistré en DB avec succès (ID: {new_doc.id})")
    
    await log_audit_action(
        db, current_user.email,
        f"Génération document: {filename} pour employee {request.employee_id}",
        "document",
        details={"document_id": new_doc.id, "employee_id": request.employee_id, "type": request.type, "filename": filename},
    )
    
    return DocumentResponse(
        id=new_doc.id,
        type=request.type,
        employee_id=request.employee_id,
        url=f"/api/documents/{new_doc.id}/download",
        created_at=new_doc.created_at,
        format=request.format
    )

@router.post("/generate/batch", response_model=BatchGenerateResponse, dependencies=[Depends(require_hr)])
def generate_documents_batch(request: BatchGenerateRequest):
    """Génération batch pour un département (Processus Asynchrone)"""
    # Stub: Envoi de la tâche dans une queue (ex: Celery)
    job_id = f"job-{uuid.uuid4()}"
    return BatchGenerateResponse(job_id=job_id, status="pending")

@router.get("/", response_model=List[UploadedDocumentResponse], dependencies=[Depends(document_access_roles)])
async def list_documents(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Liste des documents uploadés (HR/Admin voient tout, autres selon permissions)."""
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    documents = result.scalars().all()
    normalized_roles = normalize_roles(current_user.roles)
    visible_documents = documents if "hr" in normalized_roles or "admin" in normalized_roles else [
        document for document in documents if user_can_access_document(document, normalized_roles, current_user.id)
    ]
    return [await _serialize_document(db, document=document, current_user=current_user) for document in visible_documents]

@router.post("/upload", response_model=UploadedDocumentResponse, dependencies=[Depends(require_hr)])
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    try:
        validate_uploaded_document(file)
        file_content = await file.read()
        file_size = len(file_content)
        size_str = get_file_size_formatted(file_size)
        
        safe_filename = file.filename.replace(" ", "_").replace("/", "-")
        storage_uri = secure_document_storage.upload_bytes(file_content, f"{current_user.id[:8]}_{safe_filename}", "uploaded")
            
        new_doc = Document(
            name=file.filename,
            type=doc_type,
            size=size_str,
            file_path=storage_uri,
            uploaded_by=current_user.email,
            allowed_roles=["hr", "admin"],
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        
        await log_audit_action(
            db, current_user.email,
            f"Upload document: {file.filename} (type={doc_type})",
            "document",
            request,
            details={"document_id": new_doc.id, "type": doc_type, "filename": file.filename, "size": size_str},
        )
        return await _serialize_document(db, document=new_doc, current_user=current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}/viewer", response_model=DocumentViewerResponse, dependencies=[Depends(document_access_roles)])
async def get_document_viewer_metadata(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    document = await get_document_or_404(db, id)
    ensure_document_access(document, current_user)
    return await _serialize_document_viewer(db, document=document, current_user=current_user)

@router.get("/{id}/access-history", response_model=List[DocumentAccessEventResponse], dependencies=[Depends(require_hr)])
async def get_document_access_history(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    document = await get_document_or_404(db, id)
    return document.access_events

@router.put("/{id}/settings", response_model=DocumentViewerResponse, dependencies=[Depends(require_hr)])
async def update_document_settings(
    id: str,
    payload: DocumentSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    document = await get_document_or_404(db, id)
    allowed_roles = [role for role in normalize_roles(payload.allowed_roles) if role in ALL_DOCUMENT_ROLES]
    if not allowed_roles:
        raise HTTPException(status_code=400, detail="Au moins un rôle autorisé est requis.")

    document.allowed_roles = allowed_roles
    document.rag_enabled = payload.rag_enabled

    if payload.rag_enabled:
        try:
            sync_error = None
            await sync_document_to_rag(document)
            mark_document_rag_state(document, True, "ready")
            action = "rag_sync"
        except Exception as exc:
            sync_error = str(exc)
            mark_document_rag_state(document, True, "error", sync_error)
            action = "rag_sync_error"
    else:
        delete_document_from_rag(document.id)
        document.rag_status = "disabled"
        document.rag_error = None
        document.rag_last_synced_at = None
        action = "rag_disable"
        sync_error = None

    await db.commit()
    await db.refresh(document)
    await log_document_event(
        db,
        document=document,
        user_email=current_user.email,
        user_roles=current_user.roles,
        action="permissions_update",
        details={"allowed_roles": allowed_roles, "rag_enabled": payload.rag_enabled},
    )
    await log_document_event(
        db,
        document=document,
        user_email=current_user.email,
        user_roles=current_user.roles,
        action=action,
        details={"error": sync_error} if sync_error else {"allowed_roles": allowed_roles},
    )
    await log_audit(
        db, current_user.email,
        f"Mise à jour des paramètres du document: {document.name}",
        "document",
        details={
            "document_id": document.id,
            "allowed_roles": allowed_roles,
            "rag_enabled": payload.rag_enabled,
        },
    )

    return await _serialize_document_viewer(db, document=document, current_user=current_user)

@router.get("/templates", dependencies=[Depends(require_hr)])
def list_templates():
    """Liste des modèles disponibles (Administration RH)"""
    return [{"id": "tpl-1", "name": "Modèle Attestation"}]

@router.put("/templates/{id}", dependencies=[Depends(require_hr)])
def update_template(id: str):
    """Modifier un modèle"""
    return {"status": "Template updated", "id": id}

@router.get("/{id}/view", dependencies=[Depends(document_access_roles)])
async def view_document(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    document = await get_document_or_404(db, id)
    ensure_document_access(document, current_user)

    if not document_can_preview(document):
        raise HTTPException(status_code=400, detail="Prévisualisation disponible uniquement pour les PDF.")

    if not secure_document_storage.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Le fichier n'existe plus")

    await log_document_event(
        db,
        document=document,
        user_email=current_user.email,
        user_roles=current_user.roles,
        action="view",
    )
    file_bytes = secure_document_storage.download_bytes(document.file_path)
    return StreamingResponse(
        BytesIO(file_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{document.name}"'},
    )

@router.get("/{id}/download", dependencies=[Depends(document_access_roles)])
async def download_document(id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    """Télécharger un document physique"""
    doc = await get_document_or_404(db, id)
    ensure_document_access(doc, current_user)
    
    if not secure_document_storage.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Le fichier n'existe plus")

    if doc.status == "pending" and "hr" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Validation RH requise pour télécharger ce document.")

    await log_document_event(
        db,
        document=doc,
        user_email=current_user.email,
        user_roles=current_user.roles,
        action="download",
    )
    await log_audit(
        db, current_user.email,
        f"Téléchargement document: {doc.name}",
        "document",
        details={"document_id": doc.id, "document_name": doc.name},
    )
    file_bytes = secure_document_storage.download_bytes(doc.file_path)
    return StreamingResponse(
        BytesIO(file_bytes),
        media_type=guess_media_type(doc),
        headers={"Content-Disposition": f'attachment; filename="{doc.name}"'},
    )

@router.delete("/{id}", dependencies=[Depends(require_hr)])
async def delete_document(id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    doc = await get_document_or_404(db, id)
    await log_audit(
        db, current_user.email,
        f"Suppression document: {doc.name}",
        "document",
        critical=True,
        details={"document_id": doc.id, "document_name": doc.name},
    )
    delete_document_from_rag(doc.id)
    secure_document_storage.delete(doc.file_path)
    await db.delete(doc)
    await db.commit()
    return {"message": "Document supprimé"}

# ---- NEW ENDPOINTS FOR VALIDATION WORKFLOW ----

@router.put("/{document_id}/validate")
async def validate_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_hr),
):
    doc = await get_document_or_404(db, document_id)
    if doc.status != "pending":
        raise HTTPException(status_code=400, detail="Document is not pending validation")
        
    doc.status = "validated"
    await log_document_event(db, doc, current_user.email, ["hr"], "validation", {"action": "validated"})
    await log_audit(
        db, current_user.email,
        f"Validation du document: {doc.name}",
        "document",
        details={"document_id": doc.id, "document_name": doc.name},
    )
    await db.commit()
    return {"status": "success", "message": "Document validated successfully"}

@router.put("/{document_id}/reject")
async def reject_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_hr),
):
    doc = await get_document_or_404(db, document_id)
    if doc.status != "pending":
        raise HTTPException(status_code=400, detail="Document is not pending validation")
        
    doc.status = "rejected"
    await log_document_event(db, doc, current_user.email, ["hr"], "validation", {"action": "rejected"})
    await log_audit(
        db, current_user.email,
        f"Rejet du document: {doc.name}",
        "document",
        details={"document_id": doc.id, "document_name": doc.name},
    )
    await db.commit()
    return {"status": "success", "message": "Document rejected successfully"}
