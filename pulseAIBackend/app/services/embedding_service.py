"""
Service d'embedding vectoriel pour Pulse AI.

Supporte deux backends :
  - fastembed (local, léger ~100MB, par défaut)
  - OpenAI/OpenRouter API (distant, nécessite une clé API)
"""

import logging

from app.config import settings

logger = logging.getLogger("pulse.services.embedding")


class EmbeddingService:
    """
    Service d'encodage de texte en vecteurs denses (embeddings).
    
    Utilise fastembed par défaut (léger, pas de torch).
    Peut basculer sur l'API OpenAI/OpenRouter en alternative.
    """

    VECTOR_DIMENSION: int = 384  # BAAI/bge-small-en-v1.5

    def __init__(self, provider: str = None, model_name: str = None):
        self.provider = provider or settings.EMBEDDING_PROVIDER
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.model = None
        self._openai_client = None
        self.is_degraded = False
        logger.info(
            f"EmbeddingService initializing | provider={self.provider}, model={self.model_name}"
        )

    async def initialize(self):
        """Charger le modèle d'embedding en mémoire (appelé au startup)."""
        if self.provider == "fastembed":
            try:
                from fastembed import TextEmbedding
                self.model = TextEmbedding(model_name=self.model_name)
                # Déterminer la dimension réelle via un test
                test_embedding = list(self.model.embed(["test"]))[0]
                self.VECTOR_DIMENSION = len(test_embedding)
                logger.info(
                    f"Modèle fastembed chargé avec succès | "
                    f"model={self.model_name}, dim={self.VECTOR_DIMENSION}"
                )
            except ImportError:
                logger.error("fastembed non installé. Fallback vers le mode stub.")
                self.is_degraded = True
            except Exception as e:
                logger.error(f"Erreur lors du chargement de fastembed : {e}")
                self.is_degraded = True
        elif self.provider == "openai":
            try:
                from openai import AsyncOpenAI
                self._openai_client = AsyncOpenAI(
                    base_url=settings.LLM_API_URL,
                    api_key=settings.LLM_API_KEY or "not-needed"
                )
                self.VECTOR_DIMENSION = 1536  # text-embedding-3-small
                logger.info("EmbeddingService configuré via l'API OpenAI/OpenRouter")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du client OpenAI pour embeddings : {e}")
                self.is_degraded = True
        else:
            logger.warning(f"Provider d'embedding inconnu : {self.provider}")

    async def encode(self, text: str) -> list[float]:
        """Encoder un texte unique en vecteur dense."""
        if self.provider == "fastembed" and self.model is None:
            await self.initialize()
        if self.provider == "openai" and self._openai_client is None:
            await self.initialize()
        if self.provider == "fastembed" and self.model:
            embeddings = list(self.model.embed([text]))
            return embeddings[0].tolist()
        elif self.provider == "openai" and self._openai_client:
            response = await self._openai_client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        else:
            logger.warning("EmbeddingService.encode() appelé sans modèle chargé — retour vecteur zéro")
            self.is_degraded = True
            return [0.0] * self.VECTOR_DIMENSION

    async def encode_batch(
        self,
        texts: list[str],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> list[list[float]]:
        """Encoder un batch de textes en vecteurs denses."""
        if self.provider == "fastembed" and self.model is None:
            await self.initialize()
        if self.provider == "openai" and self._openai_client is None:
            await self.initialize()
        if self.provider == "fastembed" and self.model:
            embeddings = list(self.model.embed(texts, batch_size=batch_size))
            return [e.tolist() for e in embeddings]
        elif self.provider == "openai" and self._openai_client:
            results = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = await self._openai_client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                results.extend([d.embedding for d in response.data])
            return results
        else:
            logger.warning("EmbeddingService.encode_batch() appelé sans modèle chargé")
            self.is_degraded = True
            return [[0.0] * self.VECTOR_DIMENSION for _ in texts]

    def get_dimension(self) -> int:
        """Retourne la dimension des vecteurs produits par le modèle."""
        return self.VECTOR_DIMENSION


# Singleton pour injection
embedding_service = EmbeddingService()
