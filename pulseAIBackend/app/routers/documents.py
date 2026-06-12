import logging
import uuid
from datetime import datetime, timezone
from typing import List
import os
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

from app.schemas.document import (
    DocumentGenerateRequest, DocumentResponse, 
    BatchGenerateRequest, BatchGenerateResponse
)
from app.schemas.document_schemas import DocumentResponse as UploadedDocumentResponse
from app.models.domain import Document, Employee, Contract
from app.database import get_db
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_hr, require_any_role
from app.services.document_generator import document_generator
from sqlalchemy.orm import selectinload

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_file_size_formatted(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} Ko"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} Mo"

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger(__name__)

# Groupes de rôles pour la simplification
doc_generate_roles = require_any_role("collaborator", "manager", "hr")
collab_hr_roles = require_any_role("collaborator", "hr")

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
        file_path = document_generator.create(
            doc_type=request.type, 
            context=context,
            custom_fields=request.custom_fields
        )
    except Exception as e:
        logger.error(f"Échec de la génération du document: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du document")

    file_size_bytes = os.path.getsize(file_path)
    size_str = get_file_size_formatted(file_size_bytes)
    
    new_doc = Document(
        name=os.path.basename(file_path),
        type=request.type,
        size=size_str,
        file_path=file_path,
        uploaded_by="Moteur de génération IA"
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    logger.info(f"Document enregistré en DB avec succès (ID: {new_doc.id})")
    
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

@router.get("/", response_model=List[UploadedDocumentResponse], dependencies=[Depends(collab_hr_roles)])
async def list_documents(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Liste des documents uploadés (HR voit tout)"""
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()

@router.post("/upload", response_model=UploadedDocumentResponse, dependencies=[Depends(require_hr)])
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    try:
        file_content = await file.read()
        file_size = len(file_content)
        size_str = get_file_size_formatted(file_size)
        await file.seek(0)
        
        safe_filename = file.filename.replace(" ", "_").replace("/", "-")
        file_path = os.path.join(UPLOAD_DIR, f"{current_user.id[:8]}_{safe_filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        new_doc = Document(
            name=file.filename,
            type=doc_type,
            size=size_str,
            file_path=file_path,
            uploaded_by=current_user.email
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        
        return new_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", dependencies=[Depends(require_hr)])
def list_templates():
    """Liste des modèles disponibles (Administration RH)"""
    return [{"id": "tpl-1", "name": "Modèle Attestation"}]

@router.put("/templates/{id}", dependencies=[Depends(require_hr)])
def update_template(id: str):
    """Modifier un modèle"""
    return {"status": "Template updated", "id": id}

@router.get("/{id}/download", dependencies=[Depends(collab_hr_roles)])
async def download_document(id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    """Télécharger un document physique"""
    result = await db.execute(select(Document).filter(Document.id == id))
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
        
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Le fichier n'existe plus")
        
    return FileResponse(path=doc.file_path, filename=doc.name)

@router.delete("/{id}", dependencies=[Depends(require_hr)])
async def delete_document(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).filter(Document.id == id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    await db.delete(doc)
    await db.commit()
    return {"message": "Document supprimé"}