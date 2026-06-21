"""
Service de Guardrails pour Pulse AI — Gouvernance IA complète.

Catégories couvertes :
  1. SECURITY     — Prompt injection, jailbreak, extraction de données
  2. LEGAL        — RGPD, harcèlement, discrimination, diffamation
  3. HR_POLICY    — Hors périmètre RH, conseils médicaux/juridiques
  4. ETHICS       — Biais, contenu offensant, manipulation
  5. COMPLIANCE   — Normes internationales (ISO 27001, GDPR, EU AI Act)

Chaque déclenchement est loggé vers Wazuh pour supervision SIEM.
"""
import re
import json
import logging
import socket
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.domain import Guardrail

logger = logging.getLogger("pulse.services.guardrails")

# ─── Wazuh Syslog Config ────────────────────────────────────────────────────
WAZUH_HOST = "wazuh-manager"
WAZUH_PORT = 514

# ─── Guardrails par défaut ──────────────────────────────────────────────────
DEFAULT_GUARDRAILS = [
    # ── SECURITY ──
    {
        "name": "Prompt Injection - Ignore instructions",
        "category": "security",
        "pattern": r"ignore\s+(previous|all|prior)\s+instructions?|forget\s+everything|new\s+persona|act\s+as\s+(if\s+you\s+are|a\s+different)|you\s+are\s+now\s+|pretend\s+(you\s+are|to\s+be)",
        "action": "block",
        "description": "Détecte les tentatives de prompt injection classiques",
        "priority": 100,
    },
    {
        "name": "Prompt Injection - Jailbreak DAN",
        "category": "security",
        "pattern": r"DAN|do\s+anything\s+now|jailbreak|bypass\s+(your\s+)?(restrictions?|rules?|guidelines?)|without\s+(any\s+)?(restrictions?|limitations?|filters?)",
        "action": "block",
        "description": "Bloque les tentatives de jailbreak connues",
        "priority": 100,
    },
    {
        "name": "Extraction données système",
        "category": "security",
        "pattern": r"system\s+prompt|your\s+instructions?|reveal\s+your|show\s+me\s+your\s+(prompt|config|system)|what\s+are\s+your\s+(instructions?|rules?|constraints?)",
        "action": "block",
        "description": "Bloque les tentatives d'extraction de configuration interne",
        "priority": 95,
    },
    {
        "name": "Injection de code malveillant",
        "category": "security",
        "pattern": r"<script|javascript:|eval\(|exec\(|__import__|os\.system|subprocess|shell=True|\bSELECT\b.*\bFROM\b|\bDROP\s+TABLE\b|\bINSERT\s+INTO\b",
        "action": "block",
        "description": "Détecte les injections SQL, XSS et code malveillant",
        "priority": 100,
    },

    # ── LEGAL & RGPD ──
    {
        "name": "RGPD - Données personnelles tiers",
        "category": "legal",
        "pattern": r"(donne[- ]moi|montre[- ]moi|accède[- ]à|retrieve|get\s+me)\s+.{0,30}(adresse|numéro\s+de\s+téléphone|email|données\s+personnelles|informations\s+privées).{0,30}(de|of|about)\s+(?!moi|me\b)",
        "action": "block",
        "description": "Bloque les demandes de données personnelles d'autres personnes (RGPD Art. 5)",
        "priority": 90,
    },
    {
        "name": "Harcèlement - Contenu discriminatoire",
        "category": "legal",
        "pattern": r"\b(nègre|bougnoule|youpin|pédé|tapette|gonzesse|bamboula|métèque|feuj|connasse|salope|pute|enculé)\b",
        "action": "block",
        "description": "Bloque les termes discriminatoires et insultants (Code du travail Art. L1132-1)",
        "priority": 95,
    },
    {
        "name": "Discrimination - Critères protégés",
        "category": "legal",
        "pattern": r"(embaucher?|recruter?|promouvoir?|licencier?|refuser?).{0,50}(parce\s+qu[' ]il|parce\s+qu[' ]elle|because\s+(he|she|they)).{0,30}(est\s+|is\s+)(femme|homme|noir|blanc|arabe|juif|musulman|chrétien|handicapé|enceinte|vieux|jeune|gay|lesbienne)",
        "action": "block",
        "description": "Détecte les demandes de discrimination basées sur des critères protégés",
        "priority": 95,
    },
    {
        "name": "Harcèlement sexuel",
        "category": "legal",
        "pattern": r"(harcèlement\s+sexuel|sexual\s+harassment|propositions?\s+sexuelles?|avances?\s+sexuelles?|commentaires?\s+(sexuels?|obscènes?|déplacés?))",
        "action": "block",
        "description": "Détecte les demandes liées au harcèlement sexuel",
        "priority": 95,
    },
    {
        "name": "Secret professionnel",
        "category": "legal",
        "pattern": r"(salaire|salary|rémunération|compensation).{0,30}(de|of|about|pour)\s+(?!moi|me|mon\s+propre|my\s+own)",
        "action": "warn",
        "description": "Avertit sur les demandes de salaires d'autres employés",
        "priority": 80,
    },
    {
        "name": "EU AI Act - Manipulation comportementale",
        "category": "legal",
        "pattern": r"(manipuler?|manipulate|influencer?\s+subtilement|subliminal|sans\s+qu[' ]ils?\s+s[' ]en\s+rende[nt]?\s+compte|without\s+them\s+knowing|coerce|contraindre)",
        "action": "block",
        "description": "Bloque les demandes de manipulation comportementale (EU AI Act Art. 5)",
        "priority": 90,
    },

    # ── HR POLICY ──
    {
        "name": "Hors périmètre - Conseils médicaux",
        "category": "hr_policy",
        "pattern": r"(diagnostic|diagnostique|symptômes?|médicaments?|prescription|traitement\s+médical|docteur|médecin|psychiatre|antidépresseur|dose\s+de|posologie)",
        "action": "block",
        "description": "Redirige vers des professionnels de santé (hors périmètre RH)",
        "priority": 85,
    },
    {
        "name": "Hors périmètre - Conseils juridiques personnels",
        "category": "hr_policy",
        "pattern": r"(comment\s+poursuivre|sue\s+my\s+employer|porter\s+plainte\s+contre|déposer\s+une\s+plainte|recours\s+judiciaire|tribunal\s+(pour|against)|avocat\s+pour\s+me\s+défendre)",
        "action": "warn",
        "description": "Avertit sur les demandes de conseils juridiques personnels",
        "priority": 75,
    },
    {
        "name": "Hors périmètre - Politique et religion",
        "category": "hr_policy",
        "pattern": r"\b(vote[rz]?\s+pour|élection|candidat\s+politique|parti\s+(politique|républicain|démocrate|socialiste|RN|LREM)|dieu\s+existe|islam\s+est|christianisme\s+est|judaïsme\s+est)\b",
        "action": "warn",
        "description": "Sujets politiques et religieux hors périmètre professionnel",
        "priority": 70,
    },
    {
        "name": "Hors périmètre - Cryptomonnaies et investissements",
        "category": "hr_policy",
        "pattern": r"\b(bitcoin|ethereum|crypto(monnaie)?|NFT|blockchain\s+invest|acheter\s+des\s+actions|trading|bourse\s+de\s+valeurs|forex)\b",
        "action": "warn",
        "description": "Conseils financiers et crypto hors périmètre RH",
        "priority": 65,
    },
    {
        "name": "Contenu adulte explicite",
        "category": "hr_policy",
        "pattern": r"\b(pornographie|contenu\s+sexuel\s+explicite|sexe\s+avec|faire\s+l[' ]amour\s+avec|masturbation|orgasme|pénis|vagin|seins?\s+nus?)\b",
        "action": "block",
        "description": "Contenu sexuellement explicite inapproprié en milieu professionnel",
        "priority": 100,
    },

    # ── ETHICS & BIAIS ──
    {
        "name": "Biais - Stéréotypes de genre",
        "category": "ethics",
        "pattern": r"(les\s+femmes\s+sont\s+(moins|plus|pas)|les\s+hommes\s+sont\s+(naturellement|toujours|moins|plus)|women\s+are\s+(naturally|less|more|not)|men\s+are\s+(better|worse|naturally))\s+(capables?|suited|adaptées?|faites?\s+pour)",
        "action": "warn",
        "description": "Détecte les stéréotypes de genre dans les décisions RH",
        "priority": 80,
    },
    {
        "name": "Biais - Âgisme",
        "category": "ethics",
        "pattern": r"(trop\s+vieux|trop\s+jeune|too\s+old|too\s+young).{0,30}(pour\s+(ce\s+)?poste|for\s+(the\s+)?job|pour\s+être\s+promu|for\s+promotion)",
        "action": "warn",
        "description": "Détecte les biais liés à l'âge dans les décisions RH",
        "priority": 80,
    },
    {
        "name": "Violence et menaces",
        "category": "ethics",
        "pattern": r"(tuer|assassiner|frapper|blesser|détruire|exploser|attentat|terrorisme|je\s+vais\s+(te|vous|lui)\s+(tuer|frapper|blesser)|kill|murder|hurt|threaten|bomb)",
        "action": "block",
        "description": "Détecte les menaces et appels à la violence",
        "priority": 100,
    },
    {
        "name": "Manipulation émotionnelle",
        "category": "ethics",
        "pattern": r"(tu\s+dois\s+m[' ]aider\s+sinon|you\s+must\s+help\s+or|je\s+vais\s+me\s+suicider|I\s+will\s+kill\s+myself|je\s+n[' ]ai\s+plus\s+envie\s+de\s+vivre)",
        "action": "block",
        "description": "Détecte les tentatives de manipulation émotionnelle - redirige vers support",
        "priority": 100,
    },

    # ── COMPLIANCE ──
    {
        "name": "ISO 27001 - Tentative d extraction credentials",
        "category": "compliance",
        "pattern": r"(mot\s+de\s+passe|password|credentials?|token|API\s+key|clé\s+API|secret\s+key).{0,30}(donne[- ]moi|montre[- ]moi|quel\s+est|what\s+is|give\s+me|show\s+me)",
        "action": "block",
        "description": "Bloque les tentatives d'extraction de credentials (ISO 27001 A.9)",
        "priority": 100,
    },
    {
        "name": "DORA - Accès systèmes critiques",
        "category": "compliance",
        "pattern": r"(accède[rz]?\s+à|connect(er)?\s+à|accès\s+à).{0,30}(base\s+de\s+données|serveur\s+de\s+production|système\s+critique|infrastructure|réseau\s+interne)",
        "action": "block",
        "description": "Bloque les demandes d'accès à des systèmes critiques (DORA)",
        "priority": 95,
    },
]


def send_to_wazuh(event: dict) -> None:
    """Envoyer un événement de sécurité à Wazuh via syslog UDP."""
    try:
        msg = json.dumps({
            "source": "pulse-ai-guardrail",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            **event
        })
        syslog_msg = f"<14>pulse-ai: {msg}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.sendto(syslog_msg.encode('utf-8'), (WAZUH_HOST, WAZUH_PORT))
        sock.close()
        logger.info(f"Événement envoyé à Wazuh: {event.get('rule_name')}")
    except Exception as e:
        logger.warning(f"Impossible d'envoyer à Wazuh: {e}")


class GuardrailResult:
    def __init__(self, passed: bool, triggered_rules: list = None, action: str = None, message: str = None):
        self.passed = passed
        self.triggered_rules = triggered_rules or []
        self.action = action
        self.message = message


class GuardrailService:

    async def get_active_guardrails(self, db: AsyncSession) -> list:
        result = await db.execute(
            select(Guardrail)
            .filter(Guardrail.is_active)
            .order_by(Guardrail.priority.desc())
        )
        return result.scalars().all()

    async def check_input(self, text: str, db: AsyncSession, user_id: str = None, user_email: str = None) -> GuardrailResult:
        logger.info(f"Vérification guardrails input (len={len(text)})")
        return await self._check_text(text, db, direction="input", user_id=user_id, user_email=user_email)

    async def check_output(self, text: str, db: AsyncSession, user_id: str = None, user_email: str = None) -> GuardrailResult:
        logger.info(f"Vérification guardrails output (len={len(text)})")
        return await self._check_text(text, db, direction="output", user_id=user_id, user_email=user_email)

    async def _check_text(self, text: str, db: AsyncSession, direction: str, user_id: str = None, user_email: str = None) -> GuardrailResult:
        guardrails = await self.get_active_guardrails(db)
        if not guardrails:
            return GuardrailResult(passed=True)

        triggered = []
        most_severe_action = None
        severity = {"redact": 1, "warn": 2, "block": 3}

        for rule in guardrails:
            try:
                try:
                    pattern = re.compile(rule.pattern, re.IGNORECASE)
                    match = pattern.search(text)
                except re.error:
                    match = rule.pattern.lower() in text.lower()

                if match:
                    triggered.append({
                        "id": rule.id,
                        "name": rule.name,
                        "action": rule.action,
                        "category": getattr(rule, 'category', 'security'),
                        "pattern": rule.pattern,
                    })

                    logger.warning(f"Guardrail déclenché | rule={rule.name} action={rule.action} direction={direction} user={user_email}")

                    # Envoyer à Wazuh
                    send_to_wazuh({
                        "event_type": "guardrail_triggered",
                        "rule_name": rule.name,
                        "rule_action": rule.action,
                        "category": getattr(rule, 'category', 'security'),
                        "direction": direction,
                        "user_id": user_id,
                        "user_email": user_email,
                        "text_preview": text[:100],
                        "severity": "high" if rule.action == "block" else "medium",
                    })

                    await db.execute(
                        update(Guardrail)
                        .where(Guardrail.id == rule.id)
                        .values(triggered_count=Guardrail.triggered_count + 1)
                    )

                    if most_severe_action is None or severity.get(rule.action, 0) > severity.get(most_severe_action, 0):
                        most_severe_action = rule.action

            except Exception as e:
                logger.error(f"Erreur évaluation guardrail {rule.name}: {e}")

        if not triggered:
            return GuardrailResult(passed=True)

        await db.commit()

        if most_severe_action == "block":
            category = triggered[0].get("category", "security")
            messages = {
                "security": "Votre message a été bloqué pour des raisons de sécurité. Veuillez reformuler.",
                "legal": "Votre demande touche à des aspects légaux sensibles et ne peut être traitée par cet assistant. Contactez votre service juridique.",
                "hr_policy": "Cette demande est hors du périmètre de l'assistant RH. Veuillez vous adresser au service concerné.",
                "ethics": "Votre message contient du contenu inapproprié et a été bloqué.",
                "compliance": "Cette demande est bloquée pour des raisons de conformité réglementaire.",
            }
            return GuardrailResult(
                passed=False,
                triggered_rules=triggered,
                action="block",
                message=messages.get(category, messages["security"])
            )
        elif most_severe_action == "warn":
            return GuardrailResult(
                passed=True,
                triggered_rules=triggered,
                action="warn",
                message="⚠️ Attention : votre question touche à un sujet sensible. Répondre reste possible mais soyez prudent."
            )
        else:
            return GuardrailResult(passed=True, triggered_rules=triggered, action="redact")

    def test_pattern(self, pattern: str, text: str) -> dict:
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            matches = compiled.findall(text)
            return {"matched": len(matches) > 0, "matches": matches[:10], "is_valid_regex": True}
        except re.error as e:
            found = pattern.lower() in text.lower()
            return {"matched": found, "matches": [pattern] if found else [], "is_valid_regex": False, "regex_error": str(e)}

    def get_default_guardrails(self) -> list:
        return DEFAULT_GUARDRAILS


guardrail_service = GuardrailService()
