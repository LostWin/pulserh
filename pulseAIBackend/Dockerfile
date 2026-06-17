# =============================================================================
# Pulse AI Backend — Production Dockerfile
# =============================================================================
# Multi-stage build pour une image légère et sécurisée.
#
# Build  : docker build -t pulse-ai-backend .
# Run    : docker run -p 8000:8000 --env-file .env pulse-ai-backend
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 : Dépendances (cache optimisé)
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS dependencies

WORKDIR /app

# Installer les dépendances système nécessaires (compilation de certains packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev libcairo2-dev pkg-config python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 : Image finale (légère)
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Installer uniquement les libs runtime (pas les headers de compilation)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl libcairo2 pango1.0-tools postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copier les packages Python installés depuis le stage précédent
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Créer un utilisateur non-root pour la sécurité
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copier le code applicatif
COPY . .

# Donner les droits à l'utilisateur non-root
RUN chown -R appuser:appuser /app

USER appuser

# Port exposé
EXPOSE 8000

# Health check intégré au container
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Démarrer avec 4 workers Uvicorn pour la production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
