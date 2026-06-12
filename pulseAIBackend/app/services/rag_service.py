"""
Service RAG (Retrieval-Augmented Generation) pour Pulse AI.

Pipeline :
  1. Encoder la question via EmbeddingService
  2. Recherche sémantique dans Qdrant (top-K chunks pertinents)
  3. Construire le prompt avec contexte + guardrails
  4. Appeler le LLM via LLMClient
  5. Retourner la réponse + sources

Dépendances attendues :
  - EmbeddingService (sentence-transformers)
  - Qdrant (vector store)
  - LLMClient (vLLM / OpenAI)

À implémenter par : Équipe IA / NLP
"""

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger("pulse.services.rag")


class RAGService:
    """
    Service de Retrieval-Augmented Generation.

    Orchestre le pipeline complet : embedding → recherche → LLM → réponse.
    Applique les guardrails de sécurité (filtrage des rôles, anonymisation).

    Usage dans les routers :
        rag = RAGService()
        result = await rag.answer(question="...", user_role="collaborator", user_id="...")
    """

    def __init__(self):
        """
        Initialiser les clients nécessaires :
        - self.embedding_service = EmbeddingService()
        - self.qdrant_client = QdrantClient(host=settings.QDRANT_HOST)
        - self.llm_client = LLMClient()
        """
        logger.info("RAGService initialized (stub mode)")

    async def answer(
        self,
        question: str,
        user_role: str | list[str],
        user_id: str,
        conversation_id: str | None = None,
        max_sources: int = 5,
    ) -> dict[str, Any]:
        """
        Répondre à une question en utilisant le pipeline RAG complet.

        Args:
            question: La question posée par l'utilisateur.
            user_role: Rôle(s) Keycloak de l'utilisateur (pour filtrage RBAC des documents).
            user_id: Identifiant unique de l'utilisateur.
            conversation_id: ID de conversation pour le contexte multi-tour (optionnel).
            max_sources: Nombre maximum de sources à retourner.

        Returns:
            dict contenant :
                - answer (str): La réponse générée par le LLM.
                - sources (list[str]): Liste des documents sources utilisés.
                - confidence (float): Score de confiance (0.0 - 1.0).
                - tokens_used (int): Nombre de tokens consommés.

        Pipeline à implémenter :
            1. embedding = await self.embedding_service.encode(question)
            2. chunks = await self.qdrant_client.search(
                   collection_name="pulse_documents",
                   query_vector=embedding,
                   limit=max_sources,
                   query_filter=Filter(
                       must=[FieldCondition(key="access_roles", match=MatchAny(any=user_role))]
                   )
               )
            3. context = "\\n".join([chunk.payload["text"] for chunk in chunks])
            4. prompt = self._build_prompt(question, context, user_role)
            5. answer = await self.llm_client.generate(prompt)
            6. return {"answer": answer, "sources": [...], ...}

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        # --- STUB : Retour mock pour le développement ---
        logger.warning(
            f"RAGService.answer() called in STUB mode | "
            f"user_id={user_id}, question_length={len(question)}"
        )

        return {
            "answer": (
                "Ceci est une réponse fictive générée par le modèle RAG. "
                "Le pipeline complet (embedding → Qdrant → LLM) n'est pas encore implémenté."
            ),
            "sources": ["politique_rh.pdf", "conges_payes_wiki.md"],
            "confidence": 0.0,
            "tokens_used": 0,
        }

        # --- PRODUCTION : Décommenter ci-dessous ---
        # raise NotImplementedError(
        #     "RAGService.answer() n'est pas encore implémenté. "
        #     "Voir la docstring pour le pipeline complet."
        # )

    async def search_documents(
        self,
        query: str,
        user_role: str | list[str],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Recherche sémantique pure (sans génération LLM).

        Utile pour la fonctionnalité "recherche de documents" dans l'interface.

        Args:
            query: Texte de recherche.
            user_role: Rôle(s) pour le filtrage RBAC.
            top_k: Nombre de résultats à retourner.

        Returns:
            Liste de dicts avec : title, snippet, score, source_file.

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "RAGService.search_documents() n'est pas encore implémenté."
        )

    def _build_prompt(
        self, question: str, context: str, user_role: str | list[str]
    ) -> str:
        """
        Construire le prompt système avec guardrails.

        Le prompt doit inclure :
        - Instruction système (rôle de l'assistant, limites)
        - Contexte documentaire (chunks Qdrant)
        - Guardrails de sécurité (ne pas révéler de données confidentielles
          au-delà du rôle de l'utilisateur)
        - La question de l'utilisateur

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "RAGService._build_prompt() n'est pas encore implémenté."
        )


# Singleton pour injection dans les routers
rag_service = RAGService()