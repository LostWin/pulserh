from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any

from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import DocumentType, BaseTemplate, DocumentTemplate

router = APIRouter(
    prefix="/templates",
    tags=["Templates"],
    responses={404: {"description": "Not found"}},
)

# ---- DOCUMENT TYPES ----

@router.get("/types", response_model=List[Dict[str, Any]])
async def list_document_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DocumentType))
    types = result.scalars().all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "code": t.code,
            "allowed_roles": t.allowed_roles,
            "responsible_role": t.responsible_role,
            "required_variables": t.required_variables,
        }
        for t in types
    ]

@router.post("/types")
async def create_document_type(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    doc_type = DocumentType(
        name=payload["name"],
        code=payload["code"],
        allowed_roles=payload.get("allowed_roles", []),
        responsible_role=payload.get("responsible_role"),
        required_variables=payload.get("required_variables", []),
    )
    db.add(doc_type)
    await db.commit()
    return {"status": "success", "id": doc_type.id}

@router.put("/types/{id}")
async def update_document_type(id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    doc_type = (await db.execute(select(DocumentType).filter_by(id=id))).scalar_one_or_none()
    if not doc_type:
        raise HTTPException(status_code=404, detail="Type not found")
        
    doc_type.name = payload.get("name", doc_type.name)
    doc_type.code = payload.get("code", doc_type.code)
    doc_type.allowed_roles = payload.get("allowed_roles", doc_type.allowed_roles)
    doc_type.responsible_role = payload.get("responsible_role", doc_type.responsible_role)
    doc_type.required_variables = payload.get("required_variables", doc_type.required_variables)
    
    await db.commit()
    return {"status": "success", "id": doc_type.id}

@router.delete("/types/{id}")
async def delete_document_type(id: str, db: AsyncSession = Depends(get_db)):
    doc_type = (await db.execute(select(DocumentType).filter_by(id=id))).scalar_one_or_none()
    if not doc_type:
        raise HTTPException(status_code=404, detail="Type not found")
    await db.delete(doc_type)
    await db.commit()
    return {"status": "deleted"}

# ---- BASE TEMPLATES ----

@router.get("/base", response_model=List[Dict[str, Any]])
async def list_base_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BaseTemplate))
    templates = result.scalars().all()
    return [{"id": t.id, "name": t.name, "html_content": t.html_content} for t in templates]

@router.post("/base")
async def create_base_template(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    base_tpl = BaseTemplate(name=payload["name"], html_content=payload["html_content"])
    db.add(base_tpl)
    await db.commit()
    return {"status": "success", "id": base_tpl.id}

@router.delete("/base/{id}")
async def delete_base_template(id: str, db: AsyncSession = Depends(get_db)):
    base_tpl = (await db.execute(select(BaseTemplate).filter_by(id=id))).scalar_one_or_none()
    if not base_tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(base_tpl)
    await db.commit()
    return {"status": "deleted"}

# ---- DOCUMENT TEMPLATES ----

@router.get("/active", response_model=List[Dict[str, Any]])
async def list_document_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DocumentTemplate).options(
            selectinload(DocumentTemplate.document_type),
            selectinload(DocumentTemplate.base_template)
        )
    )
    templates = result.scalars().all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "document_type_id": t.document_type_id,
            "document_type_name": t.document_type.name if t.document_type else None,
            "base_template_id": t.base_template_id,
            "base_template_name": t.base_template.name if t.base_template else None,
            "html_content": t.html_content,
            "is_active": t.is_active,
        }
        for t in templates
    ]

@router.post("/active")
async def create_document_template(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    # Désactiver les autres templates pour ce type si is_active est True
    is_active = payload.get("is_active", False)
    if is_active:
        await db.execute(
            DocumentTemplate.__table__.update().where(
                DocumentTemplate.document_type_id == payload["document_type_id"]
            ).values(is_active=False)
        )
        
    tpl = DocumentTemplate(
        name=payload["name"],
        document_type_id=payload["document_type_id"],
        base_template_id=payload["base_template_id"],
        html_content=payload["html_content"],
        is_active=is_active,
    )
    db.add(tpl)
    await db.commit()
    return {"status": "success", "id": tpl.id}

@router.delete("/active/{id}")
async def delete_document_template(id: str, db: AsyncSession = Depends(get_db)):
    tpl = (await db.execute(select(DocumentTemplate).filter_by(id=id))).scalar_one_or_none()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(tpl)
    await db.commit()
    return {"status": "deleted"}

# ---- TEMPLATE ASSETS ----
from app.models.domain import TemplateAsset
from fastapi import UploadFile, File, Form
import base64

@router.get("/assets", response_model=List[Dict[str, Any]])
async def list_template_assets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TemplateAsset))
    assets = result.scalars().all()
    return [
        {
            "id": a.id,
            "key": a.key,
            "value": a.value,
            "asset_type": a.asset_type
        }
        for a in assets
    ]

@router.post("/assets")
async def create_template_asset(
    key: str = Form(...),
    asset_type: str = Form(...),
    value: str = Form(None),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    final_value = value
    if asset_type == "image_base64" and file:
        content = await file.read()
        b64 = base64.b64encode(content).decode("utf-8")
        mime = file.content_type or "image/png"
        final_value = f"data:{mime};base64,{b64}"
    elif asset_type == "text" and not final_value:
        raise HTTPException(status_code=400, detail="Text assets require a value.")

    # Check if key exists
    existing = (await db.execute(select(TemplateAsset).filter_by(key=key))).scalar_one_or_none()
    if existing:
        existing.value = final_value
        existing.asset_type = asset_type
        asset = existing
    else:
        asset = TemplateAsset(key=key, value=final_value, asset_type=asset_type)
        db.add(asset)
        
    await db.commit()
    return {"status": "success", "id": asset.id}

@router.delete("/assets/{id}")
async def delete_template_asset(id: str, db: AsyncSession = Depends(get_db)):
    asset = (await db.execute(select(TemplateAsset).filter_by(id=id))).scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await db.delete(asset)
    await db.commit()
    return {"status": "deleted"}
