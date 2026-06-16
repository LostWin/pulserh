"""
Point d'entrée principal de l'application Pulse AI Backend.

Contient :
- Configuration CORS (origines depuis .env)
- Handlers d'exceptions globaux (format uniforme)
- Enregistrement des middlewares (logging, rate limiting)
- Instrumentation Prometheus
- Inclusion de tous les routeurs
"""

from contextlib import asynccontextmanager
import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers import (
    auth, chat, documents, employees, departments,
    workflows, predictions, alerts, dashboard, admin, health, leaves, onboarding, interviews, reports, user_settings, skills, trainings, projects, talent_insights, employee_programs,
)
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.config import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# Lifespan (startup / shutdown)
# ═══════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Pulse AI API without blocking warmup tasks.")
    yield
    logger.info("Closing connection pools...")
    logger.info("Cleaning up resources...")


# ═══════════════════════════════════════════════════════════════════════════
# Application FastAPI & Configuration Swagger (OpenAPI)
# ═══════════════════════════════════════════════════════════════════════════

tags_metadata = [
    {"name": "Auth", "description": "Opérations d'authentification et de gestion de profil."},
    {"name": "Employees", "description": "Gestion des employés (CRUD, import en masse)."},
    {"name": "Departments", "description": "Gestion de la structure organisationnelle."},
    {"name": "Chat", "description": "Assistant conversationnel RAG (IA)."},
    {"name": "Documents", "description": "Générateur automatique de documents RH."},
    {"name": "Workflows", "description": "Orchestrateur agentique (Onboarding/Offboarding)."},
    {"name": "Predictions", "description": "Modèles prédictifs (Risque de départ, Turnover)."},
    {"name": "Dashboard", "description": "Métriques et KPIs consolidés pour la direction."},
    {"name": "Leaves", "description": "Consultation et demandes de congés collaborateur."},
    {"name": "Onboarding", "description": "Parcours d'intégration collaborateur et ressources associées."},
    {"name": "Interviews", "description": "Planification et suivi des entretiens manager."},
    {"name": "Reports", "description": "Génération et téléchargement des rapports direction."},
    {"name": "User Settings", "description": "Préférences utilisateur, avatar et notifications."},
    {"name": "Skills", "description": "Catalogue et maîtrise des compétences collaborateur."},
    {"name": "Trainings", "description": "Catalogue, affectation et recommandations de formation."},
    {"name": "Projects", "description": "Projets d'équipe et affectations collaborateurs."},
    {"name": "Talent Insights", "description": "Engagement historisé, performance et objectifs individuels."},
    {"name": "Employee Programs", "description": "Benefits, carrière et mobilité interne."},
    {"name": "Alerts", "description": "Gestion proactive des alertes RH et de sécurité."},
    {"name": "Admin", "description": "Console d'administration (Guardrails, Logs, Config IA)."},
    {"name": "Health", "description": "Surveillance de l'état du système et des dépendances."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=f"{settings.DESCRIPTION}\n\n"
                f"### Authentication\n"
                f"Cliquez sur le bouton **Authorize** pour injecter un Bearer Token JWT généré par Keycloak.\n\n"
                f"### Architecture\n"
                f"L'API est découpée en plusieurs modules représentant les capacités du système Pulse.",
    openapi_tags=tags_metadata,
    contact={
        "name": "Équipe Pulse AI",
        "email": "support@pulse-ai.com",
    },
    swagger_ui_parameters={"persistAuthorization": True}, # Garde le token JWT en mémoire après un F5
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════════════════════
# 13.3 — Gestion des erreurs globale (format uniforme)
# ═══════════════════════════════════════════════════════════════════════════
#
# Format de réponse d'erreur uniforme :
# {
#     "error": "ERROR_CODE",
#     "message": "Description lisible",
#     "detail": "Détails techniques (optionnel)"
# }
# ═══════════════════════════════════════════════════════════════════════════

def _error_response(
    status_code: int,
    error: str,
    message: str,
    detail: str | None = None,
) -> JSONResponse:
    """Construit une réponse d'erreur au format uniforme."""
    content = {
        "error": error,
        "message": message,
    }
    if detail is not None:
        content["detail"] = detail
    return JSONResponse(status_code=status_code, content=content)


# --- 401 Unauthorized : token invalide ou absent ---
@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_handler(request: Request, exc):
    """Token JWT invalide, expiré ou absent."""
    detail = getattr(exc, "detail", None)
    return _error_response(
        status_code=401,
        error="UNAUTHORIZED",
        message="Authentication required. Token is missing or invalid.",
        detail=str(detail) if detail else None,
    )


# --- Catch-all pour toutes les HTTPException de Starlette/FastAPI ---
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler unifié pour toutes les HTTPException.
    Mappe les status codes courants à des codes d'erreur lisibles.
    """
    status_code = exc.status_code
    detail = exc.detail

    # Mapping des status codes vers les codes d'erreur normalisés
    error_map = {
        400: ("BAD_REQUEST", "The request is malformed or contains invalid data."),
        401: ("UNAUTHORIZED", "Authentication required. Token is missing or invalid."),
        403: ("FORBIDDEN", "Insufficient permissions to access this resource."),
        404: ("NOT_FOUND", "The requested resource was not found."),
        405: ("METHOD_NOT_ALLOWED", "This HTTP method is not allowed on this endpoint."),
        409: ("CONFLICT", "The request conflicts with the current state of the resource."),
        422: ("VALIDATION_ERROR", "The request data failed validation."),
        429: ("RATE_LIMITED", "Too many requests. Please slow down."),
    }

    error_code, default_message = error_map.get(
        status_code,
        ("SERVER_ERROR", "An unexpected error occurred."),
    )

    # Pour les 5xx, loguer l'erreur
    if status_code >= 500:
        logger.error(
            f"HTTP {status_code} on {request.method} {request.url.path}: {detail}",
        )
        error_code = "INTERNAL_SERVER_ERROR"
        default_message = "An internal server error occurred. Please try again later."

    return _error_response(
        status_code=status_code,
        error=error_code,
        message=default_message,
        detail=str(detail) if detail else None,
    )


# --- 422 Unprocessable Entity : erreurs de validation Pydantic ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """
    Erreurs de validation Pydantic (body, query params, path params).
    Transforme les erreurs techniques Pydantic en format lisible.
    """
    errors = exc.errors()

    # Construire un résumé lisible des erreurs de validation
    error_details = []
    for err in errors:
        loc = " → ".join(str(part) for part in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        error_details.append(f"{loc}: {msg}")

    logger.warning(
        f"Validation error on {request.method} {request.url.path}: "
        f"{len(errors)} error(s)",
    )

    return _error_response(
        status_code=422,
        error="VALIDATION_ERROR",
        message="The request data failed validation.",
        detail="; ".join(error_details) if error_details else str(errors),
    )


# --- 500 Internal Server Error : erreur non gérée (catch-all) ---
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all pour les exceptions non gérées.
    Logue le traceback complet et retourne un message générique
    (ne pas exposer les détails internes au client).
    """
    logger.critical(
        f"Unhandled exception on {request.method} {request.url.path}: "
        f"{type(exc).__name__}: {exc}\n"
        f"{traceback.format_exc()}",
    )

    return _error_response(
        status_code=500,
        error="INTERNAL_SERVER_ERROR",
        message="An internal server error occurred. Please try again later.",
        detail=None,  # Ne JAMAIS exposer les détails d'une erreur interne
    )


# ═══════════════════════════════════════════════════════════════════════════
# 13.4 — Configuration CORS (origines depuis .env)
# ═══════════════════════════════════════════════════════════════════════════

# Parse les origines depuis la variable d'environnement (séparées par des virgules)
cors_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]


# ═══════════════════════════════════════════════════════════════════════════
# Middlewares Custom
# ═══════════════════════════════════════════════════════════════════════════

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# CORS doit être ajouté EN DERNIER pour être exécuté EN PREMIER (Starlette LIFO)
# Cela garantit que les requêtes OPTIONS preflight reçoivent les headers CORS
# avant d'être interceptées par le rate limiting ou le logging.
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)


# ═══════════════════════════════════════════════════════════════════════════
# Routeurs
# ═══════════════════════════════════════════════════════════════════════════
from app.routers import (
    imports, audit, manager
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(employees.router)
app.include_router(leaves.router)
app.include_router(onboarding.router)
app.include_router(interviews.router)
app.include_router(reports.router)
app.include_router(user_settings.router)
app.include_router(skills.router)
app.include_router(trainings.router)
app.include_router(projects.router)
app.include_router(talent_insights.router)
app.include_router(employee_programs.router)
app.include_router(departments.router)
app.include_router(workflows.router)
app.include_router(predictions.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(manager.router)
app.include_router(admin.router)
app.include_router(imports.router)
app.include_router(audit.router)
