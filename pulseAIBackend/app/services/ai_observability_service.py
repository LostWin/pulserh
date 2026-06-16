import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.domain import AIObservabilityEvent

logger = logging.getLogger(__name__)

class AIObservabilityService:
    async def log_event(
        self,
        db: AsyncSession,
        user_id: str | None,
        event_type: str,
        status: str,
        duration_ms: int | None = None,
        tokens_used: int | None = 0,
        details_json: dict | None = None,
    ) -> None:
        """Enregistre un événement d'observabilité IA en base de données."""
        try:
            event = AIObservabilityEvent(
                user_id=user_id,
                event_type=event_type,
                status=status,
                duration_ms=duration_ms,
                tokens_used=tokens_used,
                details_json=details_json or {},
            )
            db.add(event)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log AI observability event: {e}")

ai_observability_service = AIObservabilityService()
