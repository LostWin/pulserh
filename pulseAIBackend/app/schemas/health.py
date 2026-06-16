from pydantic import BaseModel
from typing import Literal

class ServiceStatus(BaseModel):
    status: Literal["ok", "down", "degraded"]
    latency_ms: int
    message: str

class ServicesHealth(BaseModel):
    postgres: ServiceStatus
    redis: ServiceStatus
    minio: ServiceStatus
    qdrant: ServiceStatus
    keycloak: ServiceStatus
    llm: ServiceStatus
    horilla: ServiceStatus
    embeddings: ServiceStatus

class DetailedHealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy", "degraded"]
    services: ServicesHealth
