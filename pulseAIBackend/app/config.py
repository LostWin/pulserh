from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pulse AI Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend pour l'application Pulse AI"

    # Bases de données & Services
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/pulse_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_DOCUMENTS_UPLOAD_BUCKET: str = "pulse-documents-uploaded"
    MINIO_DOCUMENTS_GENERATED_BUCKET: str = "pulse-documents-generated"
    MINIO_USER_ASSETS_BUCKET: str = "pulse-user-assets"
    DOCUMENTS_ENCRYPTION_KEY: str = ""

    # Sécurité (Keycloak)
    KEYCLOAK_ISSUER: str = "https://auth.pulse.local/realms/pulse"
    KEYCLOAK_JWKS_URI: str = "http://pulse_keycloak:8080/realms/pulse/protocol/openid-connect/certs"
    KEYCLOAK_INTERNAL_URL: str = "http://pulse_keycloak:8080"
    KEYCLOAK_REALM: str = "pulse"
    KEYCLOAK_ADMIN_REALM: str = "master"
    KEYCLOAK_ADMIN_CLIENT_ID: str = "admin-cli"
    KEYCLOAK_ADMIN_USERNAME: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = ""
    KEYCLOAK_DEFAULT_PASSWORD: str = "PulseRH@2026!"
    KEYCLOAK_DEFAULT_REQUIRED_ACTION: str = "UPDATE_PASSWORD"

    # CORS — origines autorisées (séparées par des virgules)
    CORS_ORIGINS: str = "https://ai.pulse.local,https://app.pulse.local,http://localhost:3000,http://localhost:5173"

    # ── LLM Provider ──
    LLM_PROVIDER: str = "openrouter"  # "openrouter" | "ollama"
    LLM_API_KEY: str = ""             # Clé OpenRouter (placeholder)
    LLM_MODEL: str = "mistralai/mistral-7b-instruct"
    LLM_API_URL: str = "https://openrouter.ai/api/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"

    # ── Embeddings ──
    EMBEDDING_PROVIDER: str = "fastembed"  # "fastembed" | "openai"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # ── Predictions ──
    PREDICTION_MODEL_VERSION: str = "v2.0"

    # ── Qdrant (Vector Store) ──
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "pulse_documents"

    # API Externes
    HORILLA_API_URL: str = "http://horilla-server/api"
    WAZUH_SYSLOG_HOST: str = "wazuh-server"
    CALENDAR_PROVIDER: str = "internal"  # internal | google | microsoft
    CALENDAR_DEFAULT_MEETING_HOUR: int = 10
    CALENDAR_LOOKAHEAD_DAYS: int = 14
    MICROSOFT_TENANT_ID: str = ""
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_GRAPH_BASE_URL: str = "https://graph.microsoft.com/v1.0"
    GOOGLE_CLIENT_EMAIL: str = ""
    GOOGLE_PRIVATE_KEY: str = ""
    GOOGLE_CALENDAR_SCOPES: str = "https://www.googleapis.com/auth/calendar"
    GOOGLE_CALENDAR_IMPERSONATION_USER: str = ""
    OFFBOARDING_CONNECTOR_PROVIDER: str = "internal"  # internal | webhook | itsm
    OFFBOARDING_WEBHOOK_URL: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_GLOBAL: int = 100      # Requêtes par fenêtre (global)
    RATE_LIMIT_CHAT: int = 30         # Requêtes par fenêtre (/chat)
    RATE_LIMIT_WINDOW: int = 60       # Fenêtre en secondes
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
