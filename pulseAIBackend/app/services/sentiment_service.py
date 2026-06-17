"""
Service d'analyse de sentiment sur les feedbacks RH.

Mode heuristique : classification par mots-clés configurables (positif/négatif).
Mode ML         : modèle CamemBERT/DistilBERT pré-entraîné avec pipeline HuggingFace.
                  Anonymisation PII obligatoire avant inférence.
                  Résultats agrégés par équipe — jamais exposés individuellement.
"""
import json
import logging
import re
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Entités PII à anonymiser avant toute inférence ML
PII_PATTERNS = [
    (r'\b[A-Z][a-zéèêëàâùûüîïôç]{2,}\s+[A-Z][a-zéèêëàâùûüîïôç]{2,}\b', '[NOM]'),   # Prénom Nom
    (r'\b[\w.+-]+@[\w-]+\.[\w.]+\b', '[EMAIL]'),                                          # Email
    (r'\b0[67]\d{8}\b', '[TEL]'),                                                         # Téléphone FR
]


def _anonymize_text(text: str) -> str:
    """Remplace les PII détectées par des tokens neutres."""
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def _sentiment_to_score(label: str, score: float) -> dict:
    """Normalise le label HuggingFace en sentiment standard."""
    label_lower = label.lower()
    if "positive" in label_lower or "5 stars" in label_lower or "4 stars" in label_lower:
        sentiment = "positive"
    elif "negative" in label_lower or "1 star" in label_lower or "2 stars" in label_lower:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"sentiment": sentiment, "confidence": round(score, 3)}


class SentimentService:
    """Analyse de sentiment sur les commentaires et feedbacks RH."""

    def __init__(self):
        self.pipeline = None

    def load(self) -> None:
        """Charge le pipeline HuggingFace depuis le cache local."""
        try:
            from transformers import pipeline as hf_pipeline
            config_model = "cmarkea/distilcamembert-base-sentiment"
            self.pipeline = hf_pipeline(
                "text-classification",
                model=config_model,
                tokenizer=config_model,
                top_k=None,
                truncation=True,
                max_length=512,
            )
            logger.info(f"Pipeline de sentiment chargé : {config_model}")
        except Exception as e:
            logger.warning(f"Pipeline sentiment non chargé — mode heuristique utilisé : {e}")

    async def _get_config(self, db: AsyncSession):
        from app.models.domain import MLModuleConfig
        result = await db.execute(
            select(MLModuleConfig).where(MLModuleConfig.module_id == "SENTIMENT")
        )
        return result.scalar_one_or_none()

    async def analyze_department_sentiment(
        self, department_id: str, db: AsyncSession, limit: int = 50
    ) -> dict:
        """
        Analyse le sentiment agrégé des commentaires d'un département.
        RGPD : résultats uniquement agrégés, jamais individuels.
        """
        from app.models.domain import EngagementSnapshot, Employee

        config = await self._get_config(db)
        mode = config.mode if config else "heuristic"

        # Récupérer les commentaires récents du département (agrégé, anonymisé)
        emp_ids = (await db.execute(
            select(Employee.id).where(
                Employee.department_id == department_id,
                Employee.status == "actif"
            )
        )).scalars().all()

        if not emp_ids:
            return _empty_sentiment(department_id, mode)

        snapshots = (await db.execute(
            select(EngagementSnapshot.comment, EngagementSnapshot.score)
            .where(
                and_(
                    EngagementSnapshot.employee_id.in_(emp_ids),
                    EngagementSnapshot.comment.is_not(None),
                )
            )
            .order_by(EngagementSnapshot.captured_at.desc())
            .limit(limit)
        )).all()

        if not snapshots:
            return _empty_sentiment(department_id, mode)

        comments = [row.comment for row in snapshots if row.comment]

        if mode == "ml" and self.pipeline is not None:
            return await self._analyze_ml(department_id, comments, config)
        else:
            if mode == "ml":
                logger.warning("Pipeline ML absent — fallback heuristique sentiment")
            return self._analyze_heuristic(department_id, comments, config)

    def _analyze_heuristic(self, department_id: str, comments: List[str], config=None) -> dict:
        """Classification par mots-clés configurables."""
        params = (config.heuristic_params or {}) if config else {}
        neg_kw = [kw.lower() for kw in params.get("negative_keywords", [
            "démission", "burn-out", "surcharge", "injuste", "épuisement"
        ])]
        pos_kw = [kw.lower() for kw in params.get("positive_keywords", [
            "motivation", "excellent", "évolution", "fier", "satisfait"
        ])]

        counts = {"positive": 0, "negative": 0, "neutral": 0}
        for comment in comments:
            c = comment.lower()
            neg_hits = sum(1 for kw in neg_kw if kw in c)
            pos_hits = sum(1 for kw in pos_kw if kw in c)
            if neg_hits > pos_hits:
                counts["negative"] += 1
            elif pos_hits > neg_hits:
                counts["positive"] += 1
            else:
                counts["neutral"] += 1

        total = len(comments)
        return {
            "department_id": department_id,
            "mode": "heuristic",
            "sample_size": total,
            "distribution": {k: round(v / total, 3) for k, v in counts.items()},
            "dominant_sentiment": max(counts, key=counts.get),
            "at_risk": counts["negative"] / total > (
                float(config.alert_threshold) if config else 0.50
            ),
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _analyze_ml(self, department_id: str, comments: List[str], config=None) -> dict:
        """Classification via pipeline HuggingFace, avec anonymisation PII."""
        params = (config.ml_params or {}) if config else {}
        should_anonymize = bool(params.get("anonymize_before_inference", True))

        processed = [_anonymize_text(c) if should_anonymize else c for c in comments]

        try:
            results = self.pipeline(processed)
            counts = {"positive": 0, "negative": 0, "neutral": 0}
            for result in results:
                top = max(result, key=lambda x: x["score"])
                normalized = _sentiment_to_score(top["label"], top["score"])
                counts[normalized["sentiment"]] += 1

            total = len(comments)
            alert_threshold = float(config.alert_threshold if config else 0.50)
            return {
                "department_id": department_id,
                "mode": "ml",
                "model": params.get("model_name", "cmarkea/distilcamembert-base-sentiment"),
                "sample_size": total,
                "pii_anonymized": should_anonymize,
                "distribution": {k: round(v / total, 3) for k, v in counts.items()},
                "dominant_sentiment": max(counts, key=counts.get),
                "at_risk": counts["negative"] / total > alert_threshold,
                "computed_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Erreur pipeline sentiment ML : {e}")
            return self._analyze_heuristic(department_id, comments, config)


def _empty_sentiment(department_id: str, mode: str) -> dict:
    return {
        "department_id": department_id,
        "mode": mode,
        "sample_size": 0,
        "distribution": {"positive": 0, "negative": 0, "neutral": 0},
        "dominant_sentiment": "neutral",
        "at_risk": False,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


sentiment_service = SentimentService()
