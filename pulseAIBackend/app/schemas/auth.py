from pydantic import BaseModel, Field
from typing import List, Optional

class LoginRequest(BaseModel):
    username: str = Field(..., description="Identifiant ou email de l'utilisateur", json_schema_extra={"example": "walid.traore@pulse.local"})
    password: str = Field(..., description="Mot de passe en clair", json_schema_extra={"example": "MotDePasseSécurisé123!"})

class CurrentUser(BaseModel):
    id: str = Field(..., description="ID unique de l'utilisateur (issu de Keycloak)", json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"})
    email: str = Field(..., description="Adresse email", json_schema_extra={"example": "walid.traore@pulse.local"})
    roles: List[str] = Field(default=[], description="Liste des rôles RBAC assignés", json_schema_extra={"example": ["collaborator", "manager"]})
    department: Optional[str] = Field(None, description="Département de rattachement", json_schema_extra={"example": "Ressources Humaines"})
    username: Optional[str] = Field(None, description="Nom d'utilisateur Keycloak", json_schema_extra={"example": "walid.traore"})
    first_name: Optional[str] = Field(None, description="Prénom issu du token", json_schema_extra={"example": "Walid"})
    last_name: Optional[str] = Field(None, description="Nom issu du token", json_schema_extra={"example": "Traore"})
    full_name: Optional[str] = Field(None, description="Nom complet issu du token", json_schema_extra={"example": "Walid Traore"})

class TokenVerifyRequest(BaseModel):
    token: str = Field(..., description="Token JWT à vérifier", json_schema_extra={"example": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIn0..."})

class CurrentUserResponse(CurrentUser):
    pass
