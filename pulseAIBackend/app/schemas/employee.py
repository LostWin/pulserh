from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class ErrorLine(BaseModel):
    line: int = Field(..., description="Numéro de la ligne en erreur dans le fichier", json_schema_extra={"example": 42})
    error: str = Field(..., description="Description de l'erreur", json_schema_extra={"example": "Format d'email invalide"})

class ImportReport(BaseModel):
    processed: int = Field(..., description="Nombre total de lignes traitées", json_schema_extra={"example": 100})
    created: int = Field(..., description="Nombre d'employés créés avec succès", json_schema_extra={"example": 90})
    updated: int = Field(..., description="Nombre d'employés mis à jour", json_schema_extra={"example": 5})
    errors: List[ErrorLine] = Field(..., description="Liste des erreurs rencontrées durant l'import")

class ImportRequest(BaseModel):
    source: str = Field("manual", description="Source de l'import", json_schema_extra={"example": "csv_upload"})

class EmployeeBase(BaseModel):
    first_name: str = Field(..., description="Prénom usuel", json_schema_extra={"example": "Walid"})
    last_name: str = Field(..., description="Nom de famille", json_schema_extra={"example": "Traoré"})
    email: EmailStr = Field(..., description="Email professionnel unique", json_schema_extra={"example": "walid.traore@pulse.local"})
    department: Optional[str] = Field(None, description="Nom ou ID du département de rattachement", json_schema_extra={"example": "IT"})
    status: str = Field("actif", description="Statut actuel dans l'entreprise (actif, inactif, suspendu)", json_schema_extra={"example": "actif"})
    contract_type: Optional[str] = Field(None, description="Type de contrat (CDI, CDD, Alternance)", json_schema_extra={"example": "CDI"})
    manager_id: Optional[str] = Field(None, description="ID de l'employé manager direct", json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"})

class EmployeeCreate(EmployeeBase):
    salary: Optional[float] = Field(None, description="Salaire brut annuel", json_schema_extra={"example": 45000.0})

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, description="Prénom usuel", json_schema_extra={"example": "Walid-Amine"})
    last_name: Optional[str] = Field(None, description="Nom de famille", json_schema_extra={"example": "Traoré"})
    email: Optional[EmailStr] = Field(None, description="Email professionnel unique", json_schema_extra={"example": "wa.traore@pulse.local"})
    department: Optional[str] = Field(None, description="Nom ou ID du département de rattachement", json_schema_extra={"example": "Finance"})
    status: Optional[str] = Field(None, description="Statut actuel dans l'entreprise", json_schema_extra={"example": "inactif"})
    contract_type: Optional[str] = Field(None, description="Type de contrat", json_schema_extra={"example": "CDI"})
    manager_id: Optional[str] = Field(None, description="ID du nouveau manager")
    salary: Optional[float] = Field(None, description="Nouveau salaire brut annuel", json_schema_extra={"example": 50000.0})

class EmployeeResponse(EmployeeBase):
    id: str = Field(..., description="ID unique généré par le système", json_schema_extra={"example": "emp-12345"})
    salary: Optional[float] = Field(None, description="Salaire brut annuel (masqué si l'utilisateur n'a pas les droits HR)", json_schema_extra={"example": 45000.0})
    phone: Optional[str] = Field(None, description="Numéro de téléphone")
    hire_date: Optional[str] = Field(None, description="Date d'embauche formatisée")
    manager_name: Optional[str] = Field(None, description="Nom complet du manager")
    leave_balance: Optional[str] = Field(None, description="Solde de congés restant")

class EmployeeListResponse(BaseModel):
    items: List[EmployeeResponse] = Field(..., description="Liste des employés correspondant aux critères")
    total: int = Field(..., description="Nombre total d'employés correspondant aux critères", json_schema_extra={"example": 150})
    page: int = Field(..., description="Numéro de la page actuelle", json_schema_extra={"example": 1})
    page_size: int = Field(..., description="Nombre d'éléments par page", json_schema_extra={"example": 20})

class ChangeRequest(BaseModel):
    field: str = Field(..., description="Nom du champ à modifier", json_schema_extra={"example": "last_name"})
    new_value: str = Field(..., description="Nouvelle valeur souhaitée", json_schema_extra={"example": "Traoré-Diallo"})