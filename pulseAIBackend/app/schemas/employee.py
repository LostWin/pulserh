from pydantic import BaseModel, ConfigDict, EmailStr, Field
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
    job_title: Optional[str] = Field(None, description="Intitulé du poste", json_schema_extra={"example": "Responsable RH"})
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
    job_title: Optional[str] = Field(None, description="Intitulé du poste", json_schema_extra={"example": "HR Business Partner"})
    status: Optional[str] = Field(None, description="Statut actuel dans l'entreprise", json_schema_extra={"example": "inactif"})
    contract_type: Optional[str] = Field(None, description="Type de contrat", json_schema_extra={"example": "CDI"})
    manager_id: Optional[str] = Field(None, description="ID du nouveau manager")
    salary: Optional[float] = Field(None, description="Nouveau salaire brut annuel", json_schema_extra={"example": 50000.0})

class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID unique généré par le système", json_schema_extra={"example": "emp-12345"})
    salary: Optional[float] = Field(None, description="Salaire brut annuel (masqué si l'utilisateur n'a pas les droits HR)", json_schema_extra={"example": 45000.0})
    phone: Optional[str] = Field(None, description="Numéro de téléphone")
    hire_date: Optional[str] = Field(None, description="Date d'embauche formatisée")
    manager_name: Optional[str] = Field(None, description="Nom complet du manager")
    leave_balance: Optional[str] = Field(None, description="Solde de congés restant")
    engagement_score: Optional[int] = Field(None, description="Score d'engagement calculé")
    risk_level: Optional[str] = Field(None, description="Niveau de risque low/medium/high")
    risk_score: Optional[int] = Field(None, description="Score de risque agrégé")
    trend_delta: Optional[int] = Field(None, description="Évolution récente estimée")
    last_active_label: Optional[str] = Field(None, description="Dernière activité estimée")
    project_count: Optional[int] = Field(None, description="Nombre de projets actifs")
    performance_score: Optional[float] = Field(None, description="Score de performance agrégé")
    focus_objective_title: Optional[str] = Field(None, description="Objectif prioritaire du moment")
    focus_objective_progress_pct: Optional[int] = Field(None, description="Progression de l'objectif prioritaire")
    benefits_status: Optional[str] = Field(None, description="Statut benefits collaborateur")
    mobility_status: Optional[str] = Field(None, description="Dernier statut de mobilité interne")
    field_visibility: Optional[dict[str, str]] = Field(None, alias="_field_visibility", description="Visibilité effective des champs")

class EmployeeListResponse(BaseModel):
    items: List[EmployeeResponse] = Field(..., description="Liste des employés correspondant aux critères")
    total: int = Field(..., description="Nombre total d'employés correspondant aux critères", json_schema_extra={"example": 150})
    page: int = Field(..., description="Numéro de la page actuelle", json_schema_extra={"example": 1})
    page_size: int = Field(..., description="Nombre d'éléments par page", json_schema_extra={"example": 20})

class ChangeRequest(BaseModel):
    field: str = Field(..., description="Nom du champ à modifier", json_schema_extra={"example": "last_name"})
    new_value: str = Field(..., description="Nouvelle valeur souhaitée", json_schema_extra={"example": "Traoré-Diallo"})

class EmployeeImportCSV(BaseModel):
    id: str
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    hire_date: Optional[str] = None
    status: str
    department_id: Optional[str] = None
    job_id: Optional[str] = None
    manager_id: Optional[str] = None


class EmployeeSkillBadge(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency_level: Optional[str] = None


class EmployeeCompetencyItem(BaseModel):
    name: str
    status: str


class EmployeeAccomplishmentItem(BaseModel):
    title: str
    desc: str
    icon: str


class EmployeeBenefitItem(BaseModel):
    plan_name: str
    category: str
    provider: Optional[str] = None
    status: str
    tier_label: Optional[str] = None
    renewal_date_label: Optional[str] = None
    employer_contribution: Optional[float] = None
    coverage_summary: Optional[str] = None


class EmployeeCareerPathItem(BaseModel):
    target_title: str
    readiness_level: str
    next_step: Optional[str] = None
    mentor_name: Optional[str] = None
    last_reviewed_at_label: Optional[str] = None


class EmployeeMobilityItem(BaseModel):
    request_type: str
    status: str
    target_department: Optional[str] = None
    target_job_title: Optional[str] = None
    requested_at_label: Optional[str] = None
    rationale: Optional[str] = None


class EmployeePromotionItem(BaseModel):
    previous_job_title: Optional[str] = None
    new_job_title: str
    effective_date_label: str
    notes: Optional[str] = None


class EmployeeProfileSummaryResponse(BaseModel):
    profile_title: Optional[str] = None
    avatar_data_url: Optional[str] = None
    birth_date_label: Optional[str] = None
    address_label: Optional[str] = None
    work_location_label: Optional[str] = None
    manager_name: Optional[str] = None
    skills: List[EmployeeSkillBadge]
    competencies: List[EmployeeCompetencyItem]
    accomplishments: List[EmployeeAccomplishmentItem]
    benefits: List[EmployeeBenefitItem] = []
    career_paths: List[EmployeeCareerPathItem] = []
    mobility_requests: List[EmployeeMobilityItem] = []
    promotions: List[EmployeePromotionItem] = []
