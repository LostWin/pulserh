from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token
from app.schemas.auth import CurrentUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """
    Dépendance récupérant l'utilisateur connecté depuis le token JWT.
    Extrait l'ID, l'email, les rôles Keycloak et le département.
    """
    try:
        payload = verify_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = payload.get("sub")
    email = payload.get("email", "")
    department = payload.get("department") # Claim personnalisé
    
    # Extraction des rôles Keycloak
    realm_access = payload.get("realm_access", {})
    roles = realm_access.get("roles", [])
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token does not contain user ID"
        )
        
    return CurrentUser(
        id=user_id,
        email=email,
        roles=roles,
        department=department
    )
