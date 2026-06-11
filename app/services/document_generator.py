"""
Service de génération de documents RH pour Pulse AI.

Pipeline : template Jinja2 → rendu PDF/DOCX → stockage MinIO → URL présignée.

À implémenter par : Équipe Backend / Documents
"""

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger("pulse.services.document_generator")


class DocumentGenerator:
    """
    Génère des documents RH (attestations, certificats, contrats, etc.).

    Usage :
        generator = DocumentGenerator()
        url = await generator.generate("attestation_travail", "emp-123", "pdf")
    """

    MINIO_BUCKET = "pulse-documents"
    TEMPLATES_DIR = "app/templates/documents"

    def __init__(self):
        """
        À initialiser :
        - self.minio_client = Minio(settings.MINIO_ENDPOINT)
        - self.jinja_env = jinja2.Environment(loader=FileSystemLoader(...))
        - self.llm_client = LLMClient()
        """
        logger.info("DocumentGenerator initialized (stub mode)")

    async def generate(
        self,
        doc_type: str,
        employee_id: str,
        format: str = "pdf",
        custom_fields: dict[str, Any] | None = None,
    ) -> str:
        """
        Générer un document RH et le stocker sur MinIO.

        Pipeline :
            1. employee = await horilla_client.get_employee(employee_id)
            2. template = self.jinja_env.get_template(f"{doc_type}.j2")
            3. rendered = template.render({**employee.dict(), **(custom_fields or {})})
            4. file_bytes = weasyprint.HTML(string=rendered).write_pdf()
            5. minio_client.put_object(BUCKET, object_name, file_bytes)
            6. return presigned_url

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            f"DocumentGenerator.generate() non implémenté. "
            f"doc_type={doc_type}, employee_id={employee_id}"
        )

    async def generate_batch(
        self, doc_type: str, department_id: str, format: str = "pdf"
    ) -> str:
        """
        Génération batch pour un département (async via Celery/ARQ).
        Retourne un job_id pour le suivi.
        """
        raise NotImplementedError(
            "DocumentGenerator.generate_batch() non implémenté."
        )

    async def list_templates(self) -> list[dict[str, str]]:
        """Lister les templates disponibles."""
        raise NotImplementedError(
            "DocumentGenerator.list_templates() non implémenté."
        )

    async def get_presigned_url(self, object_name: str, expires_hours: int = 24) -> str:
        """Obtenir une URL présignée MinIO pour un document existant."""
        raise NotImplementedError(
            "DocumentGenerator.get_presigned_url() non implémenté."
        )


# Singleton
document_generator = DocumentGenerator()