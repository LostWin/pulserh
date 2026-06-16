from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Employee, WorkflowStep
from app.services.keycloak_admin_service import keycloak_admin_service


@dataclass
class OffboardingActionResult:
    status: str
    reference: str | None = None
    details: str | None = None


class OffboardingConnector:
    async def revoke_access(self, db: AsyncSession, employee: Employee) -> OffboardingActionResult:
        if employee.user_id:
            await keycloak_admin_service.set_enabled(employee.user_id, False)
            return OffboardingActionResult(status="done", reference=f"keycloak:{employee.user_id}", details="Compte Keycloak désactivé.")
        return OffboardingActionResult(status="done", details="Aucun compte utilisateur rattaché.")

    async def register_asset_recovery(self, db: AsyncSession, employee: Employee, step: WorkflowStep) -> OffboardingActionResult:
        reference = step.external_ticket_id or f"ASSET-{employee.id[:8].upper()}-{step.sequence}"
        step.external_ticket_id = reference
        return OffboardingActionResult(status="done", reference=reference, details="Ticket interne de restitution matériel généré.")

    async def create_knowledge_transfer(self, db: AsyncSession, employee: Employee, step: WorkflowStep) -> OffboardingActionResult:
        reference = step.external_ticket_id or f"KT-{employee.id[:8].upper()}-{step.sequence}"
        step.external_ticket_id = reference
        return OffboardingActionResult(status="done", reference=reference, details="Référence de transfert de connaissances créée.")

    async def close_hr_record(self, db: AsyncSession, employee: Employee) -> OffboardingActionResult:
        employee.status = "inactif"
        for contract in employee.contracts:
            if contract.is_active:
                contract.is_active = False
                contract.end_date = contract.end_date or date.today()
        return OffboardingActionResult(status="done", details="Statut RH clôturé et contrats actifs fermés.")


offboarding_connector = OffboardingConnector()
