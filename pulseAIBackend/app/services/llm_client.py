"""
Client LLM pour Pulse AI.

Interface unifiée pour appeler un LLM via le SDK OpenAI.
Supporte OpenRouter (défaut), Ollama, vLLM, et tout backend compatible OpenAI.
"""

import logging
from typing import AsyncIterator

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger("pulse.services.llm")


class LLMClient:
    """
    Client pour les appels au LLM via le SDK OpenAI (compatible OpenRouter, Ollama, vLLM).
    
    Fournit une interface unifiée pour la génération de texte,
    avec support du streaming, du chat multi-tour et du tool-calling.
    """

    def __init__(
        self,
        provider: str = None,
        model: str = None,
        api_key: str = None,
        api_url: str = None,
    ):
        """
        Initialiser le client LLM.
        
        Auto-configure le base_url selon le provider :
        - openrouter → https://openrouter.ai/api/v1
        - ollama → http://localhost:11434/v1
        """
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL
        self.api_key = api_key or settings.LLM_API_KEY
        
        # Déterminer le base_url selon le provider
        if api_url:
            self.api_url = api_url
        elif self.provider == "openrouter":
            self.api_url = "https://openrouter.ai/api/v1"
        elif self.provider == "ollama":
            self.api_url = settings.OLLAMA_BASE_URL
        else:
            self.api_url = settings.LLM_API_URL
        
        # Initialisation du client OpenAI (SDK compatible)
        extra_headers = {}
        if self.provider == "openrouter":
            extra_headers = {
                "HTTP-Referer": "https://pulse-rh.ai",
                "X-Title": "PulseRH AI Assistant",
            }
        
        self.client = AsyncOpenAI(
            base_url=self.api_url,
            api_key=self.api_key or "not-needed",
            default_headers=extra_headers if extra_headers else None,
        )
        
        logger.info(
            f"LLMClient initialisé | provider={self.provider}, "
            f"model={self.model}, api_url={self.api_url}"
        )

    def reconfigure(self, provider: str, model: str, api_key: str = None):
        """Reconfigurer le client LLM dynamiquement (appelé depuis l'admin)."""
        logger.info(f"Reconfiguration du LLMClient : provider={provider}, model={model}")
        self.__init__(provider=provider, model=model, api_key=api_key)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 500,
        system_prompt: str = None,
        stop: list[str] = None,
    ) -> str:
        """Générer une réponse complète (non-streaming)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"LLM generate() appelé | model={self.model}, prompt_len={len(prompt)}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )
            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0
            logger.info(f"LLM generate() terminé | tokens={tokens}")
            return content
        except Exception as e:
            logger.error(f"Erreur LLM generate() : {e}")
            raise

    async def stream(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 500,
        system_prompt: str = None,
    ) -> AsyncIterator[str]:
        """Générer une réponse en streaming (SSE)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"LLM stream() appelé | model={self.model}")
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Erreur LLM stream() : {e}")
            raise

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 500,
    ) -> str:
        """Conversation multi-tour avec historique complet."""
        logger.info(f"LLM chat() appelé | model={self.model}, messages_count={len(messages)}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Erreur LLM chat() : {e}")
            raise

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> dict:
        """
        Appel LLM avec tool-calling (function calling).
        
        Retourne un dict avec :
        - "content": str ou None (réponse texte)
        - "tool_calls": list ou None (appels d'outils demandés par l'IA)
        - "usage": dict avec total_tokens
        """
        logger.info(f"LLM chat_with_tools() | model={self.model}, tools_count={len(tools)}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            choice = response.choices[0]
            result = {
                "content": choice.message.content,
                "tool_calls": None,
                "usage": {
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }
            
            if choice.message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                ]
                logger.info(
                    f"L'IA a demandé {len(result['tool_calls'])} appel(s) d'outils : "
                    f"{[tc['function']['name'] for tc in result['tool_calls']]}"
                )
            
            return result
        except Exception as e:
            logger.error(f"Erreur LLM chat_with_tools() : {e}")
            # Si le modèle ne supporte pas le tool-calling, fallback sur le chat classique
            if "tool" in str(e).lower() or "function" in str(e).lower():
                logger.warning("Le modèle ne supporte pas le tool-calling, fallback sur chat()")
                content = await self.chat(messages, temperature, max_tokens)
                return {"content": content, "tool_calls": None, "usage": {"total_tokens": 0}}
            raise

    async def health_check(self) -> bool:
        """Vérifier que le backend LLM est accessible."""
        try:
            response = await self.client.models.list()
            logger.info(f"LLM health check OK | {len(response.data)} modèle(s) disponibles")
            return True
        except Exception as e:
            logger.warning(f"LLM health check échoué : {e}")
            return False


# Singleton pour injection
llm_client = LLMClient()