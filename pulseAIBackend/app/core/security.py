from jose import jwt, JWTError
from app.config import settings

def verify_token(token: str) -> dict:
    """
    Valide la signature JWT avec la clé publique Keycloak,
    vérifie l'expiration et l'issuer.
    """
    # Si la clé n'inclut pas les en-têtes PEM, on les ajoute
    pub_key = settings.KEYCLOAK_PUBLIC_KEY
    if not pub_key.startswith("-----BEGIN"):
        pub_key = f"-----BEGIN PUBLIC KEY-----\n{pub_key}\n-----END PUBLIC KEY-----"
        
    try:
        payload = jwt.decode(
            token,
            pub_key,
            algorithms=["RS256"],
            issuer=settings.KEYCLOAK_ISSUER,
            options={"verify_aud": False} # Désactivé si l'audience ne correspond pas strictement
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token validation failed: {str(e)}")
