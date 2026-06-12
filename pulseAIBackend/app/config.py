from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pulse AI Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend pour l'application Pulse AI"

    # Bases de données & Services
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/pulse_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "localhost:9000"

    # Sécurité (Keycloak)
    KEYCLOAK_ISSUER: str = "https://auth.pulse.local/realms/pulse"
    KEYCLOAK_JWKS_URI: str = "http://pulse_keycloak:8080/realms/pulse/protocol/openid-connect/certs"

    # CORS — origines autorisées (séparées par des virgules)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ── LLM Provider ──
    LLM_PROVIDER: str = "openrouter"  # "openrouter" | "ollama"
    LLM_API_KEY: str = ""             # Clé OpenRouter (placeholder)
    LLM_MODEL: str = "mistralai/mistral-7b-instruct"
    LLM_API_URL: str = "https://openrouter.ai/api/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"

    # ── Embeddings ──
    EMBEDDING_PROVIDER: str = "fastembed"  # "fastembed" | "openai"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # ── Qdrant (Vector Store) ──
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "pulse_documents"

    # API Externes
    HORILLA_API_URL: str = "http://horilla-server/api"
    WAZUH_SYSLOG_HOST: str = "wazuh-server"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    RATE_LIMIT_GLOBAL: int = 100      # Requêtes par fenêtre (global)
    RATE_LIMIT_CHAT: int = 30         # Requêtes par fenêtre (/chat)
    RATE_LIMIT_WINDOW: int = 60       # Fenêtre en secondes
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
