"""
Service de Guardrails pour Pulse AI.

Vérifie les entrées utilisateur et les sorties IA contre des règles
de filtrage configurables depuis l'interface admin.

Supporte :
- Patterns regex
- Mots-clés exacts
- Actions : block (bloquer), warn (avertir), redact (masquer)
"""

import re
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.domain import Guardrail

logger = logging.getLogger("pulse.services.guardrails")


class GuardrailResult:
    """Résultat de la vérification d'un guardrail."""
    def __init__(self, passed: bool, triggered_rules: list = None, action: str = None, message: str = None):
        self.passed = passed
        self.triggered_rules = triggered_rules or []
        self.action = action
        self.message = message


class GuardrailService:
    """Service de vérification des guardrails IA."""

    async def get_active_guardrails(self, db: AsyncSession) -> list[Guardrail]:
        """Récupérer toutes les règles actives depuis la DB, triées par priorité."""
        result = await db.execute(
            select(Guardrail)
            .filter(Guardrail.is_active == True)
            .order_by(Guardrail.priority.desc())
        )
        return result.scalars().all()

    async def check_input(self, text: str, db: AsyncSession) -> GuardrailResult:
        """Vérifier le message de l'utilisateur contre les guardrails actifs."""
        logger.info(f"Vérification guardrails sur l'input (longueur={len(text)})")
        return await self._check_text(text, db, direction="input")

    async def check_output(self, text: str, db: AsyncSession) -> GuardrailResult:
        """Vérifier la réponse de l'IA avant envoi au client."""
        logger.info(f"Vérification guardrails sur l'output (longueur={len(text)})")
        return await self._check_text(text, db, direction="output")

    async def _check_text(self, text: str, db: AsyncSession, direction: str) -> GuardrailResult:
        """Logique commune de vérification."""
        guardrails = await self.get_active_guardrails(db)
        
        if not guardrails:
            return GuardrailResult(passed=True)
        
        triggered = []
        most_severe_action = None
        
        for rule in guardrails:
            try:
                # Essayer comme regex d'abord, sinon traiter comme mot-clé exact
                try:
                    pattern = re.compile(rule.pattern, re.IGNORECASE)
                    match = pattern.search(text)
                except re.error:
                    # Ce n'est pas un regex valide, traiter comme mot-clé
                    match = rule.pattern.lower() in text.lower()
                
                if match:
                    triggered.append({
                        "id": rule.id,
                        "name": rule.name,
                        "action": rule.action,
                        "pattern": rule.pattern,
                    })
                    logger.warning(
                        f"Guardrail déclenché | rule={rule.name}, action={rule.action}, "
                        f"direction={direction}"
                    )
                    
                    # Incrémenter le compteur de déclenchements
                    await db.execute(
                        update(Guardrail)
                        .where(Guardrail.id == rule.id)
                        .values(triggered_count=Guardrail.triggered_count + 1)
                    )
                    
                    # Déterminer l'action la plus sévère
                    severity = {"redact": 1, "warn": 2, "block": 3}
                    if most_severe_action is None or severity.get(rule.action, 0) > severity.get(most_severe_action, 0):
                        most_severe_action = rule.action
                        
            except Exception as e:
                logger.error(f"Erreur lors de l'évaluation du guardrail {rule.name} : {e}")
        
        if not triggered:
            return GuardrailResult(passed=True)
        
        await db.commit()
        
        if most_severe_action == "block":
            return GuardrailResult(
                passed=False,
                triggered_rules=triggered,
                action="block",
                message="Votre message a été bloqué par nos règles de sécurité. Veuillez reformuler votre question."
            )
        elif most_severe_action == "warn":
            return GuardrailResult(
                passed=True,  # On laisse passer mais avec un warning
                triggered_rules=triggered,
                action="warn",
                message="⚠️ Attention : votre question touche à un sujet sensible."
            )
        else:  # redact
            return GuardrailResult(
                passed=True,
                triggered_rules=triggered,
                action="redact",
                message=None
            )

    def test_pattern(self, pattern: str, text: str) -> dict:
        """Tester un pattern guardrail sur un texte donné (pour l'admin)."""
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            matches = compiled.findall(text)
            return {
                "matched": len(matches) > 0,
                "matches": matches[:10],
                "is_valid_regex": True,
            }
        except re.error as e:
            # Tester comme mot-clé
            found = pattern.lower() in text.lower()
            return {
                "matched": found,
                "matches": [pattern] if found else [],
                "is_valid_regex": False,
                "regex_error": str(e),
            }


# Singleton
guardrail_service = GuardrailService()
