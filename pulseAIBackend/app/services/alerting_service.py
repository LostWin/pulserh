"""
Service d'alerting pour Pulse AI.

Gère la création, la notification et le suivi des alertes :
  - Alertes RH (désengagement, turnover, absentéisme)
  - Alertes sécurité (guardrails IA, accès suspects)
  - Alertes workflow (étape échouée, timeout)

Canaux de notification :
  - Email (SMTP / SendGrid)
  - WebSocket (notifications temps réel dans l'app)
  - Wazuh Syslog (alertes sécurité)

À implémenter par : Équipe Backend / Notifications
"""

import logging
from typing import Any, Literal

from app.config import settings

logger = logging.getLogger("pulse.services.alerting")


class AlertingService:
    """
    Service de gestion des alertes et notifications.

    Usage :
        alerting = AlertingService()
        alert = await alerting.create_alert(
            type="disengagement",
            severity="critical",
            payload={"employee_id": "emp-123", "score": 0.87}
        )
        await alerting.send_notification(alert)
    """

    def __init__(self):
        """
        À initialiser :
        - Client SMTP / SendGrid pour les emails
        - Connexion WebSocket manager pour le temps réel
        - Client Syslog pour Wazuh
        - Connexion DB pour persister les alertes
        """
        logger.info("AlertingService initialized (stub mode)")

    async def create_alert(
        self,
        type: str,
        severity: Literal["low", "medium", "critical"],
        payload: dict[str, Any],
        employee_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Créer une nouvelle alerte et la persister en DB.

        Args:
            type: Type d'alerte ("disengagement", "security", "workflow_failed").
            severity: Niveau de sévérité ("low", "medium", "critical").
            payload: Données contextuelles (scores, détails, etc.).
            employee_id: ID de l'employé concerné (optionnel).

        Returns:
            dict avec : id, type, severity, message, created_at, status.

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            f"AlertingService.create_alert() non implémenté. "
            f"type={type}, severity={severity}"
        )

    async def send_notification(self, alert: dict[str, Any]) -> None:
        """
        Envoyer une notification pour une alerte donnée.

        Canaux utilisés selon la sévérité :
        - low     → WebSocket uniquement (notification in-app)
        - medium  → WebSocket + Email au manager
        - critical → WebSocket + Email manager + Email RH + Syslog Wazuh

        Args:
            alert: L'alerte à notifier (retour de create_alert).

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "AlertingService.send_notification() non implémenté."
        )

    async def resolve_alert(self, alert_id: str, resolved_by: str) -> dict[str, Any]:
        """
        Marquer une alerte comme résolue.

        Args:
            alert_id: ID de l'alerte.
            resolved_by: ID de l'utilisateur qui résout.

        Returns:
            L'alerte mise à jour.

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "AlertingService.resolve_alert() non implémenté."
        )

    async def set_action_plan(
        self, alert_id: str, description: str
    ) -> dict[str, Any]:
        """
        Associer un plan d'action à une alerte.

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "AlertingService.set_action_plan() non implémenté."
        )


# Singleton
alerting_service = AlertingService()