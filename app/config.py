from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pulse AI Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend pour l'application Pulse AI"

    # Bases de données & Services
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/pulse_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "localhost:9000"
    QDRANT_HOST: str = "localhost:6333"

    # Sécurité (Keycloak)
    KEYCLOAK_PUBLIC_KEY: str = "YOUR_PUBLIC_KEY_HERE"
    KEYCLOAK_ISSUER: str = "http://localhost:8080/realms/pulse-ai"

    # CORS — origines autorisées (séparées par des virgules)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # API Externes
    LLM_API_URL: str = "http://localhost:8000/v1" # vLLM ou OpenAI
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
