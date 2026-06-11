from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import TokenVerifyRequest, CurrentUserResponse, CurrentUser
from app.dependencies import get_current_user
from app.core.security import verify_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/verify", 
    response_model=CurrentUserResponse,
    summary="Vérifier la validité d'un token JWT",
    responses={
        401: {"description": "Token invalide, expiré ou malformé."}
    }
)
def verify_jwt_token(request: TokenVerifyRequest):
    """
    Vérifie la validité d'un token JWT fourni dans le corps de la requête
    et retourne les informations de l'utilisateur extraites du payload.
    """
    try:
        payload = verify_token(request.token)
        user_id = payload.get("sub")
        email = payload.get("email", "")
        department = payload.get("department")
        
        realm_access = payload.get("realm_access", {})
        roles = realm_access.get("roles", [])
        
        if not user_id:
             raise ValueError("Token missing user ID")
             
        return CurrentUserResponse(
            id=user_id, 
            email=email, 
            roles=roles, 
            department=department
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=str(e)
        )

@router.get(
    "/me", 
    response_model=CurrentUserResponse,
    summary="Obtenir le profil de l'utilisateur connecté",
    responses={
        401: {"description": "Authentification requise. Token manquant ou invalide."}
    }
)
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Retourne le profil de l'utilisateur connecté à partir du token
    passé en en-tête Authorization (Bearer).
    """
    return current_user