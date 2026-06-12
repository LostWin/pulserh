from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from app.models.domain import AuditLog

async def log_audit_action(
    db: AsyncSession,
    user_email: str,
    action: str,
    log_type: str,
    request: Request,
    critical: bool = False
):
    # Récupérer l'IP du client depuis la requête
    ip_address = request.client.host if request.client else "unknown"
    
    # Gérer le proxy si on est derrière Traefik/Nginx
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0]
        
    audit_log = AuditLog(
        user_email=user_email,
        action=action,
        log_type=log_type,
        ip_address=ip_address,
        critical=critical
    )
    
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    return audit_log
