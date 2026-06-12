"""
Middleware de rate limiting basé sur Redis (Token Bucket).

Deux niveaux de limitation par utilisateur (identifié par JWT sub ou IP) :
  - Global :  100 requêtes / minute
  - /chat  :   30 requêtes / minute

En cas de dépassement, retourne HTTP 429 Too Many Requests
avec le header Retry-After indiquant le délai d'attente en secondes.

Algorithme : Token Bucket implémenté via un script Lua atomique côté Redis
pour garantir la cohérence même en haute concurrence.
"""

import logging
import time
from typing import Optional, Tuple

from fastapi import Request, Response
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger("pulse.rate_limit")

# ---------------------------------------------------------------------------
# Configuration des limites
# ---------------------------------------------------------------------------

# Limite globale : 100 requêtes par fenêtre de 60 secondes
GLOBAL_RATE_LIMIT = settings.RATE_LIMIT_GLOBAL       # 100
GLOBAL_RATE_WINDOW = settings.RATE_LIMIT_WINDOW       # 60 (secondes)

# Limite spécifique /chat : 30 requêtes par fenêtre de 60 secondes
CHAT_RATE_LIMIT = settings.RATE_LIMIT_CHAT            # 30
CHAT_RATE_WINDOW = settings.RATE_LIMIT_WINDOW         # 60 (secondes)

# Préfixes des routes soumises au rate limit spécifique /chat
CHAT_ROUTE_PREFIXES = ("/chat", "/api/v1/chat")

# Routes exemptes de rate limiting (health, metrics)
EXEMPT_ROUTES = frozenset({
    "/health",
    "/health/ready",
    "/health/live",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
})

# ---------------------------------------------------------------------------
# Script Lua — Token Bucket atomique
# ---------------------------------------------------------------------------

# Ce script Lua est exécuté côté Redis pour garantir l'atomicité.
# Il implémente un sliding window counter (plus simple et efficace que
# le token bucket classique pour du rate limiting HTTP).
#
# KEYS[1] = clé du bucket
# ARGV[1] = limite max de requêtes
# ARGV[2] = fenêtre en secondes
# ARGV[3] = timestamp actuel
#
# Retourne : [allowed (0/1), remaining, retry_after_seconds]
RATE_LIMIT_LUA_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Nettoyer les entrées expirées (hors de la fenêtre glissante)
local window_start = now - window
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- Compter les requêtes dans la fenêtre courante
local current_count = redis.call('ZCARD', key)

if current_count < limit then
    -- Ajouter la requête courante (score = timestamp, member = unique)
    redis.call('ZADD', key, now, now .. '-' .. math.random(1000000))
    redis.call('EXPIRE', key, window + 1)
    return {1, limit - current_count - 1, 0}
else
    -- Calculer quand le prochain slot sera disponible
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retry_after = 0
    if #oldest >= 2 then
        retry_after = math.ceil(tonumber(oldest[2]) + window - now)
        if retry_after < 1 then retry_after = 1 end
    end
    return {0, 0, retry_after}
end
"""

# ---------------------------------------------------------------------------
# Connexion Redis (lazy singleton)
# ---------------------------------------------------------------------------

_redis_client = None
_lua_script_sha = None


async def _get_redis():
    """
    Retourne le client Redis async (singleton).
    Lazy-init pour ne pas bloquer le démarrage si Redis est down.
    """
    global _redis_client, _lua_script_sha

    if _redis_client is not None:
        return _redis_client, _lua_script_sha

    try:
        import redis.asyncio as aioredis

        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=True,
        )
        # Vérifier la connexion
        await _redis_client.ping()

        # Charger le script Lua côté Redis
        _lua_script_sha = await _redis_client.script_load(RATE_LIMIT_LUA_SCRIPT)

        logger.info("Redis connection established for rate limiting")
        return _redis_client, _lua_script_sha

    except Exception as e:
        logger.warning(f"Redis connection failed for rate limiting: {e}")
        _redis_client = None
        _lua_script_sha = None
        return None, None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_user_id(request: Request) -> Optional[str]:
    """
    Extrait le user_id du JWT (best-effort, sans vérification de signature).
    Fallback sur l'IP client si pas de token.
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token,
                key="",
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except JWTError:
            pass

    # Fallback : identifier par IP
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


def _is_chat_route(path: str) -> bool:
    """Vérifie si la route est une route /chat."""
    return any(path.startswith(prefix) for prefix in CHAT_ROUTE_PREFIXES)


async def _check_rate_limit(
    identifier: str,
    limit: int,
    window: int,
    bucket_name: str,
) -> Tuple[bool, int, int]:
    """
    Vérifie le rate limit pour un identifiant donné.

    Returns:
        (allowed, remaining, retry_after)
        - allowed: True si la requête est autorisée
        - remaining: nombre de requêtes restantes
        - retry_after: secondes avant le prochain slot (0 si autorisé)
    """
    redis_client, lua_sha = await _get_redis()

    if redis_client is None:
        # Fail-open : si Redis est down, on laisse passer
        logger.warning("Rate limiting disabled: Redis unavailable")
        return True, limit, 0

    key = f"pulse:ratelimit:{bucket_name}:{identifier}"
    now = time.time()

    try:
        result = await redis_client.evalsha(
            lua_sha,
            1,          # nombre de KEYS
            key,        # KEYS[1]
            str(limit),
            str(window),
            str(now),
        )
        allowed = bool(int(result[0]))
        remaining = int(result[1])
        retry_after = int(result[2])
        return allowed, remaining, retry_after

    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        # Fail-open en cas d'erreur
        return True, limit, 0


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware ASGI de rate limiting basé sur Redis.

    Pour chaque requête :
    1. Identifie l'utilisateur (JWT sub ou IP client)
    2. Vérifie le rate limit global (100 req/min)
    3. Si route /chat, vérifie aussi le rate limit spécifique (30 req/min)
    4. Ajoute les headers X-RateLimit-* à la réponse
    5. Retourne 429 avec Retry-After si la limite est dépassée
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path

        # Exempter les routes système
        if path in EXEMPT_ROUTES:
            return await call_next(request)

        # Identifier l'utilisateur
        identifier = _extract_user_id(request)

        # --- Vérification du rate limit GLOBAL ---
        global_allowed, global_remaining, global_retry = await _check_rate_limit(
            identifier=identifier,
            limit=GLOBAL_RATE_LIMIT,
            window=GLOBAL_RATE_WINDOW,
            bucket_name="global",
        )

        if not global_allowed:
            logger.warning(
                f"Rate limit exceeded (global): {identifier} on {path}"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please slow down.",
                    "type": "global_rate_limit",
                    "limit": GLOBAL_RATE_LIMIT,
                    "window_seconds": GLOBAL_RATE_WINDOW,
                    "retry_after": global_retry,
                },
                headers={
                    "Retry-After": str(global_retry),
                    "X-RateLimit-Limit": str(GLOBAL_RATE_LIMIT),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(global_retry),
                },
            )

        # --- Vérification du rate limit /CHAT (si applicable) ---
        chat_remaining = None
        if _is_chat_route(path):
            chat_allowed, chat_remaining, chat_retry = await _check_rate_limit(
                identifier=identifier,
                limit=CHAT_RATE_LIMIT,
                window=CHAT_RATE_WINDOW,
                bucket_name="chat",
            )

            if not chat_allowed:
                logger.warning(
                    f"Rate limit exceeded (chat): {identifier} on {path}"
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many chat requests. Please wait before sending another message.",
                        "type": "chat_rate_limit",
                        "limit": CHAT_RATE_LIMIT,
                        "window_seconds": CHAT_RATE_WINDOW,
                        "retry_after": chat_retry,
                    },
                    headers={
                        "Retry-After": str(chat_retry),
                        "X-RateLimit-Limit": str(CHAT_RATE_LIMIT),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(chat_retry),
                    },
                )

        # --- Requête autorisée : continuer ---
        response = await call_next(request)

        # Ajouter les headers de rate limit à la réponse
        response.headers["X-RateLimit-Limit"] = str(GLOBAL_RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(global_remaining)

        # Si route /chat, ajouter les headers spécifiques
        if chat_remaining is not None:
            response.headers["X-RateLimit-Limit-Chat"] = str(CHAT_RATE_LIMIT)
            response.headers["X-RateLimit-Remaining-Chat"] = str(chat_remaining)

        return response
