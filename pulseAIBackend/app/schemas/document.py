from pydantic import BaseModel
from typing import Optional, Literal
from enum import Enum
from datetime import datetime

class DocumentType(str, Enum):
    ATTESTATION_TRAVAIL = "attestation_travail"
    CERTIFICAT_SALAIRE = "certificat_salaire"
    CONTRAT_TRAVAIL = "contrat_travail"
    AVENANT_CONTRAT = "avenant_contrat"
    DEMANDE_CONGE = "demande_conge"
    LETTRE_DEMISSION = "lettre_demission"

class DocumentGenerateRequest(BaseModel):
    type: DocumentType
    employee_id: str
    format: Literal["pdf", "docx"]
    custom_fields: Optional[dict] = None

class DocumentResponse(BaseModel):
    id: str
    type: DocumentType
    employee_id: str
    url: str
    created_at: datetime
    format: str

class BatchGenerateRequest(BaseModel):
    type: DocumentType
    department_id: str
    format: Literal["pdf", "docx"]

class BatchGenerateResponse(BaseModel):
    job_id: str
    status: str