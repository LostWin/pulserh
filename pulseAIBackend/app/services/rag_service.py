"""
Service RAG (Retrieval-Augmented Generation) pour Pulse AI.

Pipeline complet :
  1. Vérifier les guardrails sur l'input
  2. Encoder la question via EmbeddingService
  3. Recherche sémantique dans Qdrant (top-K chunks pertinents, filtrage RBAC)
  4. Construire le prompt avec contexte + guardrails + outils
  5. Appeler le LLM via LLMClient (avec tool-calling)
  6. Boucle d'exécution des outils (chaînage si nécessaire)
  7. Vérifier les guardrails sur l'output
  8. Retourner la réponse + sources + tokens
"""

import json
import logging
from typing import Any, AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.services.llm_client import llm_client
from app.services.embedding_service import embedding_service
from app.services.ai_tools import TOOL_DEFINITIONS, execute_tool
from app.services.guardrail_service import guardrail_service
from app.models.domain import AIConfiguration

logger = logging.getLogger("pulse.services.rag")


class RAGService:
    """
    Service de Retrieval-Augmented Generation.
    Orchestre le pipeline complet : guardrails → embedding → recherche → LLM + tools → réponse.
    """

    def __init__(self):
        self.qdrant_client = None
        self.collection_name = settings.QDRANT_COLLECTION
        logger.info("RAGService initialized")

    async def initialize(self):
        """Initialiser la connexion Qdrant (appelé au startup)."""
        try:
            from qdrant_client import QdrantClient
            self.qdrant_client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )
            logger.info(f"Connecté à Qdrant : {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            
            # Créer la collection si elle n'existe pas
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                from qdrant_client.models import Distance, VectorParams
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=embedding_service.get_dimension(),
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Collection Qdrant '{self.collection_name}' créée (dim={embedding_service.get_dimension()})")
            else:
                logger.info(f"Collection Qdrant '{self.collection_name}' déjà existante")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Qdrant : {e}")
            self.qdrant_client = None

    async def _get_ai_config(self, db: AsyncSession) -> dict:
        """Charger la configuration IA depuis la DB."""
        result = await db.execute(select(AIConfiguration).limit(1))
        config = result.scalar_one_or_none()
        if config:
            return {
                "provider": config.provider,
                "model_name": config.model_name,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "system_prompt": config.system_prompt,
                "guardrails_enabled": config.guardrails_enabled,
            }
        # Defaults
        return {
            "provider": settings.LLM_PROVIDER,
            "model_name": settings.LLM_MODEL,
            "temperature": 0.7,
            "max_tokens": 2048,
            "system_prompt": "Tu es Pulse AI, un assistant RH intelligent. Tu aides les collaborateurs avec leurs questions sur les congés, la paie, les formations et les démarches administratives. Tu es professionnel, empathique et précis.",
            "guardrails_enabled": True,
        }

    def _build_prompt(
        self, question: str, context: str, user_role: str | list[str], system_prompt: str = None
    ) -> list[dict]:
        """
        Construire les messages pour le LLM avec contexte RAG et guardrails.
        """
        roles = user_role if isinstance(user_role, list) else [user_role]
        role_str = ", ".join(roles)
        
        base_system = system_prompt or "Tu es Pulse AI, un assistant RH intelligent."
        
        full_system = f"""{base_system}

RÈGLES DE SÉCURITÉ :
- L'utilisateur a le(s) rôle(s) : {role_str}
- Ne révèle JAMAIS d'informations salariales individuelles sauf si l'utilisateur demande les siennes propres
- Ne communique pas les données personnelles d'autres employés
- Si tu n'as pas la réponse, dis-le clairement et oriente vers le bon interlocuteur RH
- Réponds toujours en français

CONTEXTE DOCUMENTAIRE :
{context if context else "Aucun document pertinent trouvé dans la base de connaissances."}

Tu as accès à des outils qui te permettent de récupérer les données de l'employé connecté (profil, congés, contrats, présences) et de générer des documents RH. Utilise-les quand c'est pertinent pour fournir une réponse précise."""

        return [
            {"role": "system", "content": full_system},
            {"role": "user", "content": question},
        ]

    async def answer(
        self,
        question: str,
        user_role: str | list[str],
        user_id: str,
        conversation_id: str = None,
        max_sources: int = 5,
        conversation_history: list[dict] = None,
        db: AsyncSession = None,
    ) -> dict[str, Any]:
        """
        Répondre à une question en utilisant le pipeline RAG complet.

        Returns:
            dict contenant :
                - answer (str): La réponse générée par le LLM.
                - sources (list[str]): Liste des documents sources utilisés.
                - confidence (float): Score de confiance (0.0 - 1.0).
                - tokens_used (int): Nombre de tokens consommés.
                - tool_results (list): Résultats des outils utilisés.
                - warning (str|None): Message de warning guardrail.
        """
        logger.info(
            f"RAGService.answer() | user_id={user_id}, question_length={len(question)}"
        )
        
        # Charger la config IA
        ai_config = await self._get_ai_config(db) if db else {}
        
        # 1. Vérifier les guardrails sur l'input
        if db and ai_config.get("guardrails_enabled", True):
            input_check = await guardrail_service.check_input(question, db)
            if not input_check.passed:
                logger.warning(f"Message bloqué par guardrail : {input_check.triggered_rules}")
                return {
                    "answer": input_check.message,
                    "sources": [],
                    "confidence": 0.0,
                    "tokens_used": 0,
                    "tool_results": [],
                    "blocked": True,
                }
        
        # 2. Recherche sémantique dans Qdrant
        sources = []
        context = ""
        
        if self.qdrant_client:
            try:
                query_embedding = await embedding_service.encode(question)
                
                search_results = self.qdrant_client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,
                    limit=max_sources,
                ).points
                
                if search_results:
                    context_parts = []
                    for hit in search_results:
                        text = hit.payload.get("text", "")
                        source = hit.payload.get("source", "Document inconnu")
                        context_parts.append(text)
                        sources.append(source)
                    context = "\n\n---\n\n".join(context_parts)
                    logger.info(f"Qdrant : {len(search_results)} chunk(s) trouvé(s)")
                else:
                    logger.info("Qdrant : aucun résultat pertinent")
            except Exception as e:
                logger.error(f"Erreur lors de la recherche Qdrant : {e}")
        
        # 3. Construire les messages
        system_prompt = ai_config.get("system_prompt")
        messages = self._build_prompt(question, context, user_role, system_prompt)
        
        # Ajouter l'historique de conversation si disponible
        if conversation_history:
            # Insérer l'historique entre le system prompt et le dernier message user
            system_msg = messages[0]
            user_msg = messages[-1]
            messages = [system_msg] + conversation_history + [user_msg]
        
        # 4. Appel LLM avec tool-calling
        temperature = ai_config.get("temperature", 0.7)
        max_tokens = ai_config.get("max_tokens", 2048)
        total_tokens = 0
        tool_results_list = []
        
        try:
            # Tenter avec tool-calling
            result = await llm_client.chat_with_tools(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            total_tokens += result["usage"]["total_tokens"]
            
            # 5. Boucle d'exécution des outils (max 3 itérations)
            max_tool_iterations = 3
            iteration = 0
            
            while result.get("tool_calls") and iteration < max_tool_iterations and db:
                iteration += 1
                logger.info(f"Boucle d'outils — itération {iteration}")
                
                # Ajouter le message assistant avec les tool_calls
                assistant_msg = {"role": "assistant", "content": result.get("content") or ""}
                if result["tool_calls"]:
                    assistant_msg["tool_calls"] = [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": tc["function"],
                        }
                        for tc in result["tool_calls"]
                    ]
                messages.append(assistant_msg)
                
                # Exécuter chaque outil
                for tc in result["tool_calls"]:
                    tool_name = tc["function"]["name"]
                    try:
                        arguments = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    tool_result = await execute_tool(tool_name, arguments, db, user_id)
                    tool_results_list.append({
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": json.loads(tool_result) if tool_result else {},
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": tool_result,
                    })
                
                # Relancer le LLM avec les résultats des outils
                result = await llm_client.chat_with_tools(
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                total_tokens += result["usage"]["total_tokens"]
            
            answer = result.get("content") or "Je n'ai pas pu générer de réponse. Veuillez reformuler votre question."
            
        except Exception as e:
            logger.error(f"Erreur dans le pipeline RAG : {e}")
            answer = "Désolé, une erreur technique s'est produite. Veuillez réessayer dans un instant."
            
        # 6. Vérifier les guardrails sur l'output
        warning = None
        if db and ai_config.get("guardrails_enabled", True):
            output_check = await guardrail_service.check_output(answer, db)
            if not output_check.passed:
                answer = output_check.message
            elif output_check.action == "warn":
                warning = output_check.message
        
        # Dédupliquer les sources
        unique_sources = list(dict.fromkeys(sources))
        
        return {
            "answer": answer,
            "sources": unique_sources,
            "confidence": min(1.0, len(unique_sources) * 0.2) if unique_sources else 0.5,
            "tokens_used": total_tokens,
            "tool_results": tool_results_list,
            "warning": warning,
        }

    async def stream_answer(
        self,
        question: str,
        user_role: str | list[str],
        user_id: str,
        conversation_history: list[dict] = None,
        db: AsyncSession = None,
    ) -> AsyncIterator[dict]:
        """
        Répondre en streaming via SSE.
        
        Yields des dicts avec :
        - {"type": "source", "content": "nom_document.pdf"}
        - {"type": "tool_call", "content": {"tool": "...", "result": {...}}}
        - {"type": "text", "content": "fragment de texte"}
        - {"type": "done", "content": {"tokens_used": N}}
        """
        logger.info(f"RAGService.stream_answer() | user_id={user_id}")
        
        ai_config = await self._get_ai_config(db) if db else {}
        
        # 1. Guardrails input
        if db and ai_config.get("guardrails_enabled", True):
            input_check = await guardrail_service.check_input(question, db)
            if not input_check.passed:
                yield {"type": "text", "content": input_check.message}
                yield {"type": "done", "content": {"tokens_used": 0, "blocked": True}}
                return
        
        # 2. Recherche Qdrant
        sources = []
        context = ""
        
        if self.qdrant_client:
            try:
                query_embedding = await embedding_service.encode(question)
                search_results = self.qdrant_client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,
                    limit=5,
                ).points
                if search_results:
                    context_parts = []
                    for hit in search_results:
                        text = hit.payload.get("text", "")
                        source = hit.payload.get("source", "Document")
                        context_parts.append(text)
                        sources.append(source)
                        yield {"type": "source", "content": source}
                    context = "\n\n---\n\n".join(context_parts)
            except Exception as e:
                logger.error(f"Erreur Qdrant en streaming : {e}")
        
        # 3. D'abord, exécuter les outils en non-streaming
        system_prompt = ai_config.get("system_prompt")
        messages = self._build_prompt(question, context, user_role, system_prompt)
        
        if conversation_history:
            system_msg = messages[0]
            user_msg = messages[-1]
            messages = [system_msg] + conversation_history + [user_msg]
        
        temperature = ai_config.get("temperature", 0.7)
        max_tokens = ai_config.get("max_tokens", 2048)
        total_tokens = 0
        
        try:
            # Phase tool-calling (non-streaming)
            result = await llm_client.chat_with_tools(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            total_tokens += result["usage"]["total_tokens"]
            
            # Exécuter les outils si demandé
            iteration = 0
            while result.get("tool_calls") and iteration < 3 and db:
                iteration += 1
                
                assistant_msg = {"role": "assistant", "content": result.get("content") or ""}
                if result["tool_calls"]:
                    assistant_msg["tool_calls"] = [
                        {"id": tc["id"], "type": "function", "function": tc["function"]}
                        for tc in result["tool_calls"]
                    ]
                messages.append(assistant_msg)
                
                for tc in result["tool_calls"]:
                    tool_name = tc["function"]["name"]
                    try:
                        arguments = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    tool_result = await execute_tool(tool_name, arguments, db, user_id)
                    
                    yield {
                        "type": "tool_call",
                        "content": {
                            "tool": tool_name,
                            "result": json.loads(tool_result) if tool_result else {},
                        },
                    }
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": tool_result,
                    })
                
                result = await llm_client.chat_with_tools(
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                total_tokens += result["usage"]["total_tokens"]
            
            # Phase streaming — si on a un contenu final, le streamer
            if result.get("content"):
                # Le contenu est déjà complet, on le stream mot par mot pour l'effet
                words = result["content"].split(" ")
                for i, word in enumerate(words):
                    yield {"type": "text", "content": word + (" " if i < len(words) - 1 else "")}
            else:
                # Fallback : streaming direct depuis le LLM
                async for chunk in llm_client.stream(
                    prompt=question,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=messages[0]["content"],
                ):
                    yield {"type": "text", "content": chunk}
                    
        except Exception as e:
            logger.error(f"Erreur dans stream_answer : {e}")
            yield {"type": "text", "content": "Désolé, une erreur s'est produite. Veuillez réessayer."}
        
        yield {"type": "done", "content": {"tokens_used": total_tokens, "sources": sources}}

    async def search_documents(
        self,
        query: str,
        user_role: str | list[str],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Recherche sémantique pure (sans génération LLM)."""
        if not self.qdrant_client:
            logger.warning("Qdrant non initialisé — recherche impossible")
            return []
        
        try:
            query_embedding = await embedding_service.encode(query)
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
            ).points
            
            return [
                {
                    "title": hit.payload.get("title", "Document"),
                    "snippet": hit.payload.get("text", "")[:200],
                    "score": hit.score,
                    "source_file": hit.payload.get("source", "inconnu"),
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche documentaire : {e}")
            return []


# Singleton pour injection dans les routers
rag_service = RAGService()