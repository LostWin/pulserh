import json
from pathlib import Path

# Constantes pour la configuration prédictive IA
AI_PREDICTIVE_CONFIG_PATH = Path("app/data/ai_predictive_config.json")
DEFAULT_AI_PREDICTIVE_CONFIG = {
    "alertThreshold": 65,
    "absenceWeight": 1.5,
    "strictMode": False,
}

class AdminService:
    def read_ai_predictive_config(self) -> dict:
        if not AI_PREDICTIVE_CONFIG_PATH.exists():
            return DEFAULT_AI_PREDICTIVE_CONFIG.copy()
        try:
            return {**DEFAULT_AI_PREDICTIVE_CONFIG, **json.loads(AI_PREDICTIVE_CONFIG_PATH.read_text())}
        except Exception:
            return DEFAULT_AI_PREDICTIVE_CONFIG.copy()

    def write_ai_predictive_config(self, payload: dict) -> dict:
        AI_PREDICTIVE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        normalized = {
            "alertThreshold": int(payload.get("alertThreshold", DEFAULT_AI_PREDICTIVE_CONFIG["alertThreshold"])),
            "absenceWeight": float(payload.get("absenceWeight", DEFAULT_AI_PREDICTIVE_CONFIG["absenceWeight"])),
            "strictMode": bool(payload.get("strictMode", DEFAULT_AI_PREDICTIVE_CONFIG["strictMode"])),
        }
        AI_PREDICTIVE_CONFIG_PATH.write_text(json.dumps(normalized, indent=2))
        return normalized

admin_service = AdminService()
