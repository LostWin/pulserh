from jose import jwt, JWTError
import requests
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Cache en mémoire de la clé publique / JWKS
jwks_cache = None

def get_jwks():
    global jwks_cache
    if not jwks_cache:
        try:
            # Récupère les clés publiques depuis Keycloak via le réseau interne Docker
            response = requests.get(settings.KEYCLOAK_JWKS_URI, timeout=10)
            response.raise_for_status()
            jwks_cache = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS from Keycloak: {e}")
            raise ValueError("Unable to fetch public keys from Identity Provider")
    return jwks_cache

def verify_token(token: str) -> dict:
    """
    Valide la signature JWT en récupérant dynamiquement le JWKS de Keycloak,
    vérifie l'expiration et l'issuer.
    """
    jwks = get_jwks()
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=settings.KEYCLOAK_ISSUER,
            options={"verify_aud": False} # L'audience dépend du client (pulse-web / pulse-backend)
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token validation failed: {str(e)}")
