from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.domain import AuditLog
from app.schemas.audit_schemas import AuditLogResponse
from app.dependencies import get_current_user
from app.core.rbac import require_role

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)

@router.get("", response_model=List[AuditLogResponse], dependencies=[Depends(require_role("admin"))])
async def get_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(AuditLog).order_by(AuditLog.timestamp.desc())
    result = await db.execute(query)
    return result.scalars().all()
