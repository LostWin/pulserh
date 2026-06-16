import logging

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.config import settings
from app.database import get_db
from app.middleware.rate_limit import _get_redis
from app.services.keycloak_admin_service import keycloak_admin_service
from app.services.llm_client import llm_client
from app.services.rag_service import rag_service
from app.services.secure_document_storage import secure_document_storage
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.health import DetailedHealthResponse, ServicesHealth
from app.core.rbac import require_admin

# Pas de préfixe global pour pouvoir mapper facilement sur /health
router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)

@router.get("/health")
def get_health():
    """Santé globale de l'API (Public, pour Load Balancer ou Kubernetes)"""
    return {"status": "healthy"}

@router.get("/health/detailed", response_model=DetailedHealthResponse, dependencies=[Depends(require_admin)])
async def get_detailed_health(db: AsyncSession = Depends(get_db)):
    """État détaillé de chaque service dépendant (Réservé admin)"""
    import time
    from app.services.embedding_service import embedding_service
    from app.schemas.health import ServiceStatus
    
    statuses: dict[str, ServiceStatus] = {}
    
    # Postgres
    start = time.time()
    try:
        await db.execute(text("SELECT 1"))
        statuses["postgres"] = ServiceStatus(status="ok", latency_ms=int((time.time() - start)*1000), message="Connecté")
    except Exception as e:
        statuses["postgres"] = ServiceStatus(status="down", latency_ms=int((time.time() - start)*1000), message=str(e))

    # Redis
    start = time.time()
    try:
        if not settings.RATE_LIMIT_ENABLED:
            statuses["redis"] = ServiceStatus(status="ok", latency_ms=0, message="Désactivé par configuration")
        else:
            redis_client, _ = await _get_redis()
            if redis_client:
                statuses["redis"] = ServiceStatus(status="ok", latency_ms=int((time.time() - start)*1000), message="Connecté (Rate limiting global actif)")
            else:
                statuses["redis"] = ServiceStatus(status="degraded", latency_ms=int((time.time() - start)*1000), message="Fail-open actif (Redis injoignable ou en cooldown)")
    except Exception as e:
        statuses["redis"] = ServiceStatus(status="down", latency_ms=int((time.time() - start)*1000), message=str(e))

    # Minio
    start = time.time()
    try:
        secure_document_storage.ensure_ready()
        statuses["minio"] = ServiceStatus(status="ok", latency_ms=int((time.time() - start)*1000), message="Connecté")
    except Exception as e:
        statuses["minio"] = ServiceStatus(status="down", latency_ms=int((time.time() - start)*1000), message=str(e))

    # Qdrant
    start = time.time()
    try:
        if rag_service.qdrant_client:
            rag_service.qdrant_client.get_collections()
            statuses["qdrant"] = ServiceStatus(status="ok", latency_ms=int((time.time() - start)*1000), message="Connecté")
        else:
            statuses["qdrant"] = ServiceStatus(status="degraded", latency_ms=int((time.time() - start)*1000), message="Client non initialisé")
    except Exception as e:
        statuses["qdrant"] = ServiceStatus(status="down", latency_ms=int((time.time() - start)*1000), message=str(e))

    # Keycloak
    start = time.time()
    try:
        await keycloak_admin_service.list_users()
        statuses["keycloak"] = ServiceStatus(status="ok", latency_ms=int((time.time() - start)*1000), message="Connecté")
    except Exception as e:
        statuses["keycloak"] = ServiceStatus(status="down", latency_ms=int((time.time() - start)*1000), message=str(e))

    # LLM
    start = time.time()
    try:
        if llm_client.provider == "openrouter" and not settings.LLM_API_KEY:
            statuses["llm"] = ServiceStatus(status="degraded", latency_ms=int((time.time() - start)*1000), message="Clé API manquante")
        else:
            statuses["llm"] = ServiceStatus(status="ok", latency_ms=int((time.time() - start)*1000), message="Connecté")
    except Exception as e:
        statuses["llm"] = ServiceStatus(status="down", latency_ms=int((time.time() - start)*1000), message=str(e))

    # Embeddings
    start = time.time()
    try:
        if getattr(embedding_service, "is_degraded", False):
            statuses["embeddings"] = ServiceStatus(status="degraded", latency_ms=int((time.time() - start)*1000), message="Fallback stub")
        else:
            statuses["embeddings"] = ServiceStatus(status="ok", latency_ms=int((time.time() - start)*1000), message="Connecté")
    except Exception as e:
        statuses["embeddings"] = ServiceStatus(status="down", latency_ms=int((time.time() - start)*1000), message=str(e))

    # Horilla
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(settings.HORILLA_API_URL)
            if response.status_code < 500:
                statuses["horilla"] = ServiceStatus(status="ok", latency_ms=int((time.time() - start)*1000), message=f"HTTP {response.status_code}")
            else:
                statuses["horilla"] = ServiceStatus(status="degraded", latency_ms=int((time.time() - start)*1000), message=f"HTTP {response.status_code}")
    except Exception as e:
        statuses["horilla"] = ServiceStatus(status="down", latency_ms=int((time.time() - start)*1000), message=str(e))

    services = ServicesHealth(
        postgres=statuses["postgres"],
        redis=statuses["redis"],
        minio=statuses["minio"],
        qdrant=statuses["qdrant"],
        keycloak=statuses["keycloak"],
        llm=statuses["llm"],
        embeddings=statuses["embeddings"],
        horilla=statuses["horilla"],
    )
    if all(s.status == "ok" for s in statuses.values()):
        global_status = "healthy"
    elif any(s.status == "down" for s in statuses.values()):
        global_status = "unhealthy"
    else:
        global_status = "degraded"

    return DetailedHealthResponse(
        status=global_status,
        services=services
    )

# Note : L'endpoint /metrics est directement géré par `prometheus_fastapi_instrumentator` dans main.py
