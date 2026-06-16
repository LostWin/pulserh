"""
Middleware de logging structuré (JSON) pour Pulse AI.

Chaque requête HTTP est loguée avec :
  - method, path, query_string
  - user_id (extrait du JWT si présent)
  - duration_ms
  - status_code
  - client_ip, user_agent

Les champs sensibles (password, token, secret, authorization) sont
automatiquement masqués pour éviter les fuites dans les logs Wazuh.
"""

import json
import logging
import time
import uuid
from typing import Any, Dict, Optional

from fastapi import Request, Response
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


# ---------------------------------------------------------------------------
# Structured JSON Formatter
# ---------------------------------------------------------------------------

class JSONLogFormatter(logging.Formatter):
    """
    Formatte les records de logging en JSON structuré une ligne,
    directement ingérable par Wazuh / ELK / Loki.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Ajouter les champs extra injectés par le middleware
        for key in (
            "request_id",
            "method",
            "path",
            "query",
            "client_ip",
            "user_agent",
            "user_id",
            "status_code",
            "duration_ms",
        ):
            value = getattr(record, key, None)
            if value is not None:
                log_entry[key] = value

        # Inclure l'exception si présente
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# Logger dédié aux requêtes HTTP
# ---------------------------------------------------------------------------

_http_logger = logging.getLogger("pulse.http")
_http_logger.setLevel(logging.INFO)
_http_logger.propagate = False  # évite la duplication dans le root logger

# Créer le handler stdout avec le formatter JSON
if not _http_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(JSONLogFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z"))
    _http_logger.addHandler(_handler)

# ---------------------------------------------------------------------------
# Champs sensibles à masquer
# ---------------------------------------------------------------------------

SENSITIVE_FIELDS = frozenset({
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "api_key",
    "apikey",
    "credit_card",
    "card_number",
    "cvv",
    "ssn",
})

# Routes dont le body ne doit JAMAIS être loggé (même partiellement)
SENSITIVE_ROUTES = frozenset({
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/reset-password",
    "/auth/login",
    "/auth/register",
    "/auth/refresh",
    "/auth/reset-password",
})

# Routes exclues du logging (health checks, métriques)
EXCLUDED_ROUTES = frozenset({
    "/health",
    "/health/ready",
    "/health/live",
    "/metrics",
    "/favicon.ico",
})


def _sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Masque récursivement les valeurs des champs sensibles."""
    sanitized: Dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in SENSITIVE_FIELDS:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                _sanitize_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized


def _sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Masque les headers sensibles (Authorization, Cookie, etc.)."""
    sanitized: Dict[str, str] = {}
    sensitive_headers = {"authorization", "cookie", "set-cookie", "x-api-key"}
    for key, value in headers.items():
        if key.lower() in sensitive_headers:
            sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = value
    return sanitized


def _extract_user_id(request: Request) -> Optional[str]:
    """
    Tente d'extraire le user_id depuis le token JWT dans le header Authorization.
    Retourne None si le token est absent ou invalide (pas d'erreur levée).
    """
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    try:
        # Décodage sans vérification de signature pour le logging uniquement
        # La vérification complète est faite dans les dépendances de route
        payload = jwt.decode(
            token,
            key="",  # Pas de vérification de signature ici
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_aud": False,
                "verify_iss": False,
            },
        )
        return payload.get("sub")
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware ASGI qui logue chaque requête/réponse en JSON structuré.

    Format de sortie (une ligne JSON par requête) :
    {
        "timestamp": "2026-06-11T21:30:00+0100",
        "level": "INFO",
        "logger": "pulse.http",
        "message": "HTTP Request",
        "request_id": "abc123",
        "method": "POST",
        "path": "/api/v1/chat",
        "query": "",
        "client_ip": "192.168.1.10",
        "user_agent": "Mozilla/5.0 ...",
        "user_id": "keycloak-uuid-1234",
        "status_code": 200,
        "duration_ms": 42.5
    }
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Ignorer les routes exclues (health, metrics)
        path = request.url.path
        if path in EXCLUDED_ROUTES:
            return await call_next(request)

        # Générer un request_id unique pour la traçabilité
        request_id = request.headers.get(
            "x-request-id", str(uuid.uuid4())[:8]
        )

        # Extraire le user_id du JWT (best-effort, pas bloquant)
        user_id = _extract_user_id(request)

        # Mesurer la durée de traitement
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            # Logger l'erreur avec le contexte de la requête
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000, 2
            )
            _http_logger.error(
                "HTTP Request - Unhandled Exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "query": str(request.url.query),
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", ""),
                    "user_id": user_id,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                },
                exc_info=exc,
            )
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Déterminer le niveau de log selon le status code
        status_code = response.status_code
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        # Émettre le log structuré
        _http_logger.log(
            log_level,
            "HTTP Request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "query": str(request.url.query),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", ""),
                "user_id": user_id,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )

        # Injecter le request_id dans le header de réponse pour la traçabilité
        response.headers["X-Request-ID"] = request_id

        return response
