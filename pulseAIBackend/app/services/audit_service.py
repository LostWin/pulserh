"""
audit_service.py
================
Service centralisé d'audit pour PulseRH.

Toute action enregistrée est :
  1. Persistée dans la table `audit_logs` (DB audit).
  2. Émise dans les logs applicatifs via le module `logging` standard
     (format JSON-like, capturé par tout handler configuré : fichier,
     stdout, Loki, Wazuh, CloudWatch, etc.).

Fonctions exportées
-------------------
- log_audit(db, user_email, action, log_type, ...)
    Appel sans contexte HTTP — pour les actions internes, agents IA,
    tâches de fond.

- log_audit_action(db, user_email, action, log_type, request=None, ...)
    Appel avec Request FastAPI optionnel — extrait l'IP cliente si dispo.
"""

import logging
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import AuditLog

# Dédicace à l'audit : tous les messages passent par ce logger.
# Le format est lisible et parseable par Loki / ELK / Wazuh.
_audit_logger = logging.getLogger("pulserh.audit")


def _emit_log(
    user_email: str,
    action: str,
    log_type: str,
    ip_address: str,
    critical: bool,
    details: Optional[Dict[str, Any]],
) -> None:
    """Émet un message structuré dans le logger Python."""
    level = logging.WARNING if critical else logging.INFO
    _audit_logger.log(
        level,
        "[AUDIT] type=%s critical=%s user=%s ip=%s action=%r details=%s",
        log_type,
        critical,
        user_email,
        ip_address,
        action,
        details or {},
    )


async def log_audit(
    db: AsyncSession,
    user_email: str,
    action: str,
    log_type: str,
    ip_address: str = "internal",
    critical: bool = False,
    details: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """
    Enregistre une action d'audit sans contexte HTTP.

    Usage typique : services internes, agents IA, tâches de fond.
    L'IP sera fixée à "internal".
    """
    # 1. Log Python (stdout / fichier / agrégateur)
    _emit_log(user_email, action, log_type, ip_address, critical, details)

    # 2. Persistance DB
    audit_log = AuditLog(
        user_email=user_email,
        action=action,
        log_type=log_type,
        ip_address=ip_address,
        critical=critical,
        details=details,
    )
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    return audit_log


async def log_audit_action(
    db: AsyncSession,
    user_email: str,
    action: str,
    log_type: str,
    request=None,
    critical: bool = False,
    details: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """
    Enregistre une action d'audit avec Request FastAPI optionnel.

    Si `request` est fourni, l'IP réelle du client est extraite
    (en tenant compte de X-Forwarded-For pour les reverse-proxies).
    Sinon, l'IP est fixée à "internal".
    """
    ip_address = "internal"
    if request is not None:
        try:
            ip_address = request.client.host if request.client else "unknown"
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                ip_address = forwarded_for.split(",")[0].strip()
        except Exception:
            ip_address = "unknown"

    return await log_audit(
        db=db,
        user_email=user_email,
        action=action,
        log_type=log_type,
        ip_address=ip_address,
        critical=critical,
        details=details,
    )
