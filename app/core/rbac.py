from fastapi import Depends, HTTPException, status
from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser

def require_role(required_role: str):
    """
    Dépendance RBAC pour vérifier la présence d'un rôle
    spécifique dans la liste des rôles de l'utilisateur courant.
    """
    def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if required_role not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Not enough privileges. Required role: {required_role}"
            )
        return current_user
    return role_checker

def require_any_role(*required_roles: str):
    """
    Dépendance RBAC pour vérifier la présence d'au moins un rôle
    parmi la liste fournie.
    """
    def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Not enough privileges. Required one of: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

# Dépendances prêtes à l'emploi pour les routeurs
require_collaborator = require_role("collaborator")
require_manager = require_role("manager")
require_hr = require_role("hr")
require_director = require_role("director")
require_admin = require_role("admin")
