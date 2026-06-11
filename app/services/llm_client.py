"""
Client LLM pour Pulse AI.

Interface unifiée pour appeler un LLM (vLLM, OpenAI, ou compatible).
Supporte le streaming, le chat multi-tour et le contrôle de la génération.

Backends supportés (à configurer via LLM_API_URL) :
  - vLLM local : http://localhost:8000/v1
  - OpenAI     : https://api.openai.com/v1
  - Ollama     : http://localhost:11434/v1

Dépendances attendues :
  - httpx (client HTTP async)
  - openai (SDK officiel, compatible vLLM)

À implémenter par : Équipe IA / Infrastructure
"""

import logging
from typing import AsyncIterator, Optional

from app.config import settings

logger = logging.getLogger("pulse.services.llm")


class LLMClient:
    """
    Client pour les appels au LLM (vLLM / OpenAI / compatible).

    Fournit une interface unifiée pour la génération de texte,
    avec support du streaming et du chat multi-tour.

    Usage :
        llm = LLMClient()
        response = await llm.generate("Résume ce document : ...")
        async for chunk in llm.stream("Explique-moi le processus de ..."):
            print(chunk, end="")
    """

    def __init__(
        self,
        api_url: str | None = None,
        model: str = "mistral-7b-instruct",
        api_key: str | None = None,
    ):
        """
        Initialiser le client LLM.

        À implémenter :
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                base_url=api_url or settings.LLM_API_URL,
                api_key=api_key or "not-needed"  # vLLM n'exige pas de clé
            )

        Args:
            api_url: URL de l'API LLM. Défaut : settings.LLM_API_URL.
            model: Nom du modèle à utiliser.
            api_key: Clé API (requis pour OpenAI, optionnel pour vLLM).
        """
        self.api_url = api_url or settings.LLM_API_URL
        self.model = model
        self.api_key = api_key
        self.client = None  # À remplacer par AsyncOpenAI
        logger.info(
            f"LLMClient initialized (stub mode) | "
            f"api_url={self.api_url}, model={self.model}"
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 500,
        system_prompt: str | None = None,
        stop: list[str] | None = None,
    ) -> str:
        """
        Générer une réponse complète (non-streaming).

        Args:
            prompt: Le prompt utilisateur.
            temperature: Contrôle de la créativité (0.0 = déterministe, 1.0 = créatif).
            max_tokens: Nombre maximum de tokens à générer.
            system_prompt: Instruction système optionnelle (personnalité, guardrails).
            stop: Séquences d'arrêt pour stopper la génération.

        Returns:
            Le texte généré par le LLM.

        À implémenter :
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )
            return response.choices[0].message.content

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "LLMClient.generate() n'est pas encore implémenté. "
            f"Configurer le backend LLM à l'adresse : {self.api_url}"
        )

    async def stream(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 500,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """
        Générer une réponse en streaming (Server-Sent Events).

        Utile pour l'interface chat en temps réel.

        Args:
            prompt: Le prompt utilisateur.
            temperature: Contrôle de la créativité.
            max_tokens: Nombre maximum de tokens.
            system_prompt: Instruction système optionnelle.

        Yields:
            Fragments de texte au fur et à mesure de la génération.

        À implémenter :
            messages = [{"role": "user", "content": prompt}]
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "LLMClient.stream() n'est pas encore implémenté."
        )
        # yield is needed to make this an async generator
        yield ""  # noqa: unreachable

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 500,
    ) -> str:
        """
        Conversation multi-tour avec historique complet.

        Args:
            messages: Liste de messages au format OpenAI :
                [
                    {"role": "system", "content": "Tu es un assistant RH..."},
                    {"role": "user", "content": "Bonjour"},
                    {"role": "assistant", "content": "Bonjour ! Comment puis-je..."},
                    {"role": "user", "content": "Comment poser un congé ?"},
                ]
            temperature: Contrôle de la créativité.
            max_tokens: Nombre maximum de tokens.

        Returns:
            La réponse du LLM au dernier message.

        Raises:
            NotImplementedError: Ce service est un stub.
        """
        raise NotImplementedError(
            "LLMClient.chat() n'est pas encore implémenté."
        )

    async def health_check(self) -> bool:
        """
        Vérifier que le backend LLM est accessible.

        Returns:
            True si le LLM répond, False sinon.
        """
        try:
            # À implémenter : GET {api_url}/health ou models endpoint
            logger.warning("LLMClient.health_check() stub — returning False")
            return False
        except Exception:
            return False


# Singleton pour injection
llm_client = LLMClient()