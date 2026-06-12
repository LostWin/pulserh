"""
Service d'embedding vectoriel pour Pulse AI.

Responsable de la conversion de texte en vecteurs denses
pour la recherche sémantique dans Qdrant.

Modèle recommandé :
  - sentence-transformers/all-MiniLM-L6-v2 (384 dimensions, rapide)
  - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (multilingue FR/EN)

Dépendances attendues :
  - sentence-transformers
  - torch (CPU ou GPU selon l'infra)

À implémenter par : Équipe IA / NLP
"""

import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger("pulse.services.embedding")


class EmbeddingService:
    """
    Service d'encodage de texte en vecteurs denses (embeddings).

    Charge un modèle sentence-transformers en mémoire au démarrage
    et fournit des méthodes sync/async pour encoder du texte.

    Usage :
        embedding_svc = EmbeddingService()
        vector = await embedding_svc.encode("Comment poser un congé ?")
        vectors = await embedding_svc.encode_batch(["texte 1", "texte 2"])
    """

    # Dimension des vecteurs produits (dépend du modèle choisi)
    VECTOR_DIMENSION: int = 384  # all-MiniLM-L6-v2

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Charger le modèle sentence-transformers en mémoire.

        À implémenter :
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)

        Args:
            model_name: Nom du modèle HuggingFace à charger.
        """
        self.model_name = model_name
        self.model = None  # À remplacer par le modèle chargé
        logger.info(
            f"EmbeddingService initialized (stub mode) | model={model_name}"
        )

    async def encode(self, text: str) -> list[float]:
        """
        Encoder un texte unique en vecteur dense.

        Args:
            text: Le texte à encoder.

        Returns:
            Liste de floats de dimension VECTOR_DIMENSION.

        À implémenter :
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "EmbeddingService.encode() n'est pas encore implémenté. "
            "Installer sentence-transformers et charger le modèle."
        )

    async def encode_batch(
        self,
        texts: list[str],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> list[list[float]]:
        """
        Encoder un batch de textes en vecteurs denses.

        Optimisé pour l'indexation de documents (plus efficace que
        des appels individuels à encode()).

        Args:
            texts: Liste de textes à encoder.
            batch_size: Taille des batches pour l'inférence.
            show_progress: Afficher une barre de progression.

        Returns:
            Liste de vecteurs (un par texte).

        À implémenter :
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=show_progress
            )
            return embeddings.tolist()

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "EmbeddingService.encode_batch() n'est pas encore implémenté."
        )

    def get_dimension(self) -> int:
        """Retourne la dimension des vecteurs produits par le modèle."""
        return self.VECTOR_DIMENSION


# Singleton pour injection
embedding_service = EmbeddingService()