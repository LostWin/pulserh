from pydantic import BaseModel
from typing import Literal

class ServicesHealth(BaseModel):
    postgres: Literal["ok", "down", "degraded"]
    redis: Literal["ok", "down", "degraded"]
    minio: Literal["ok", "down", "degraded"]
    qdrant: Literal["ok", "down", "degraded"]
    keycloak: Literal["ok", "down", "degraded"]
    llm: Literal["ok", "down", "degraded"]
    horilla: Literal["ok", "down", "degraded"]

class DetailedHealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy", "degraded"]
    services: ServicesHealth
