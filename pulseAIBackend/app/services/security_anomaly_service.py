"""
Service de détection d'anomalies dans les usages IA (AI Observability).

Mode heuristique : seuils fixes configurables (tokens/heure, requêtes/heure, plages horaires suspectes).
Mode ML         : Isolation Forest entraîné sur les patterns d'usage normaux,
                  s'exécute en batch configurable (ex: toutes les heures).
"""
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

MODEL_BUCKET = "ml-models"
MODEL_KEY = "anomaly_isof_v1.pkl"


class SecurityAnomalyService:
    """Détecte les comportements suspects dans les événements d'observabilité IA."""

    def __init__(self):
        self.model = None

    def load(self) -> None:
        """Charge le modèle Isolation Forest depuis MinIO."""
        try:
            import io, joblib
            from minio import Minio
            from app.config import settings

            client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False,
            )
            response = client.get_object(MODEL_BUCKET, MODEL_KEY)
            self.model = joblib.load(io.BytesIO(response.read()))
            logger.info("Modèle Isolation Forest chargé depuis MinIO")
        except Exception as e:
            logger.warning(f"Modèle anomalie absent — mode heuristique utilisé : {e}")

    async def _get_config(self, db: AsyncSession):
        from app.models.domain import MLModuleConfig
        result = await db.execute(
            select(MLModuleConfig).where(MLModuleConfig.module_id == "SECURITY_ANOMALY")
        )
        return result.scalar_one_or_none()

    async def analyze_user_behavior(
        self, user_id: str, db: AsyncSession, window_hours: int = 1
    ) -> dict:
        """Analyse le comportement récent d'un utilisateur et retourne un score d'anomalie."""
        from app.models.domain import AIObservabilityEvent

        config = await self._get_config(db)
        mode = config.mode if config else "heuristic"

        since = datetime.now(timezone.utc) - timedelta(hours=window_hours)

        events = (await db.execute(
            select(AIObservabilityEvent).where(
                and_(
                    AIObservabilityEvent.user_id == user_id,
                    AIObservabilityEvent.created_at >= since,
                )
            )
        )).scalars().all()

        features = _extract_behavior_features(events, window_hours)

        if mode == "ml" and self.model is not None:
            return self._detect_ml(user_id, features, config)
        else:
            if mode == "ml":
                logger.warning("Modèle ML anomalie absent — fallback heuristique")
            return self._detect_heuristic(user_id, features, config)

    def _detect_heuristic(self, user_id: str, features: dict, config=None) -> dict:
        """Détection par seuils configurables."""
        params = (config.heuristic_params or {}) if config else {}
        max_tokens = int(params.get("max_tokens_per_hour", 50000))
        max_requests = int(params.get("max_requests_per_hour", 200))
        suspicious_start = int(params.get("suspicious_hours_start", 0))
        suspicious_end = int(params.get("suspicious_hours_end", 5))
        alert_threshold = float(config.alert_threshold if config else 0.80)

        flags = []
        score = 0.0

        if features["total_tokens"] > max_tokens:
            flags.append(f"Tokens dépassent le seuil ({features['total_tokens']} > {max_tokens})")
            score += 0.4

        if features["request_count"] > max_requests:
            flags.append(f"Requêtes dépassent le seuil ({features['request_count']} > {max_requests})")
            score += 0.4

        if features["has_suspicious_hour_activity"]:
            flags.append(f"Activité détectée sur plage suspecte ({suspicious_start}h-{suspicious_end}h)")
            score += 0.2

        if features["error_rate"] > 0.5:
            flags.append(f"Taux d'erreur élevé ({features['error_rate']:.0%})")
            score += 0.2

        score = min(score, 1.0)
        is_anomaly = score >= alert_threshold

        return {
            "user_id": user_id,
            "mode": "heuristic",
            "anomaly_score": round(score, 3),
            "is_anomaly": is_anomaly,
            "flags": flags,
            "features": features,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _detect_ml(self, user_id: str, features: dict, config=None) -> dict:
        """Détection via Isolation Forest."""
        try:
            import numpy as np

            params = (config.ml_params or {}) if config else {}
            alert_threshold = float(config.alert_threshold if config else 0.80)

            X = np.array([[
                features["total_tokens"],
                features["request_count"],
                features["error_rate"],
                float(features["has_suspicious_hour_activity"]),
                features["avg_duration_ms"],
            ]])

            # predict: -1 = anomalie, 1 = normal
            prediction = self.model.predict(X)[0]
            raw_score = self.model.score_samples(X)[0]  # Plus négatif = plus anormal
            # Normaliser entre 0 et 1 (0 = normal, 1 = très anormal)
            anomaly_score = max(0.0, min(1.0, (-raw_score) / 0.5))

            is_anomaly = prediction == -1 or anomaly_score >= alert_threshold

            return {
                "user_id": user_id,
                "mode": "ml",
                "model": "isolation_forest",
                "anomaly_score": round(anomaly_score, 3),
                "is_anomaly": is_anomaly,
                "flags": ["Comportement anormal détecté par le modèle"] if is_anomaly else [],
                "features": features,
                "computed_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Erreur détection ML anomalie : {e}")
            return self._detect_heuristic(user_id, features, config)

    async def run_batch_analysis(self, db: AsyncSession) -> List[dict]:
        """
        Analyse tous les utilisateurs actifs sur la dernière heure.
        Crée des alertes pour les comportements suspects.
        """
        from app.models.domain import AIObservabilityEvent, Alert

        config = await self._get_config(db)
        params = (config.ml_params or config.heuristic_params or {}) if config else {}
        window = int(params.get("batch_interval_minutes", 60))

        since = datetime.now(timezone.utc) - timedelta(minutes=window)

        active_users = (await db.execute(
            select(AIObservabilityEvent.user_id)
            .where(
                and_(
                    AIObservabilityEvent.user_id.is_not(None),
                    AIObservabilityEvent.created_at >= since,
                )
            )
            .distinct()
        )).scalars().all()

        results = []
        for user_id in active_users:
            try:
                analysis = await self.analyze_user_behavior(user_id, db, window_hours=window // 60 or 1)
                results.append(analysis)

                # Créer une alerte si anomalie détectée
                if analysis["is_anomaly"]:
                    alert = Alert(
                        type="SECURITY_ANOMALY",
                        severity="HIGH",
                        message=f"Comportement suspect détecté pour l'utilisateur {user_id}",
                        details_json=analysis,
                        source="SECURITY_ANOMALY_ML",
                    )
                    db.add(alert)
            except Exception as e:
                logger.error(f"Erreur analyse utilisateur {user_id}: {e}")

        await db.commit()
        return results


def _extract_behavior_features(events: list, window_hours: int) -> dict:
    """Extrait les features comportementales d'une liste d'événements."""
    if not events:
        return {
            "total_tokens": 0,
            "request_count": 0,
            "error_rate": 0.0,
            "has_suspicious_hour_activity": False,
            "avg_duration_ms": 0.0,
        }

    total_tokens = sum(e.tokens_used or 0 for e in events)
    request_count = len(events)
    errors = sum(1 for e in events if e.status == "error")
    error_rate = errors / request_count if request_count > 0 else 0.0
    avg_duration = sum(e.duration_ms or 0 for e in events) / max(request_count, 1)

    # Activité sur plages horaires nocturnes (0h-5h par défaut)
    suspicious_hours = any(
        e.created_at and 0 <= e.created_at.hour < 5
        for e in events
        if e.created_at
    )

    return {
        "total_tokens": total_tokens,
        "request_count": request_count,
        "error_rate": round(error_rate, 3),
        "has_suspicious_hour_activity": suspicious_hours,
        "avg_duration_ms": round(avg_duration, 1),
    }


security_anomaly_service = SecurityAnomalyService()
