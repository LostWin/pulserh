import logging
from fastapi import APIRouter, Depends

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
def get_detailed_health():
    """État détaillé de chaque service dépendant (Réservé admin)"""
    # Stub: Simulation de la vérification des pings des dépendances externes
    services = ServicesHealth(
        postgres="ok",
        redis="ok",
        minio="ok",
        qdrant="ok",
        keycloak="ok",
        llm="ok",
        horilla="ok"
    )
    
    return DetailedHealthResponse(
        status="healthy",
        services=services
    )

# Note : L'endpoint /metrics est directement géré par `prometheus_fastapi_instrumentator` dans main.py