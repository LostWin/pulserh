#!/bin/bash
set -e

echo "╔══════════════════════════════════════╗"
echo "║        Setup PulseRH Security        ║"
echo "╚══════════════════════════════════════╝"

# ── Vérifier les prérequis
command -v docker >/dev/null 2>&1 || { echo "❌ Docker non installé"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "❌ Docker Compose non installé"; exit 1; }

# ── Vérifier le .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  Fichier .env créé depuis .env.example"
  echo "   → Remplis les variables sensibles dans .env avant de relancer"
  exit 1
fi

# ── /etc/hosts
echo ""
echo "📝 [1/6] Configuration /etc/hosts..."
HOSTS_LINE="127.0.0.1 ai.pulse.local api.pulse.local auth.pulse.local wazuh.pulse.local grafana.pulse.local prometheus.pulse.local traefik.pulse.local"
if grep -q "ai.pulse.local" /etc/hosts; then
  echo "   ✅ Déjà configuré"
else
  echo "$HOSTS_LINE" | sudo tee -a /etc/hosts > /dev/null
  echo "   ✅ Entrées ajoutées"
fi

# ── Démarrage
echo ""
echo "🐳 [2/6] Démarrage des services Docker..."
docker compose up -d
echo "   ⏳ Attente que les services soient healthy (90s)..."
sleep 90

# ── Migrations
echo ""
echo "🗄️  [3/6] Migrations base de données..."
docker exec pulse_backend bash -c "cd /app && python -m alembic upgrade head"
echo "   ✅ Migrations appliquées"

# ── Patch audit_logs
echo ""
echo "🔧 [4/6] Patch schéma base de données..."
docker exec pulse_postgres psql -U pulse_ai_user -d pulse_ai \
  -c "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS details JSON;" 2>/dev/null && \
  echo "   ✅ Colonne details ajoutée" || echo "   ✅ Déjà présente"

# ── Wazuh
echo ""
echo "🔐 [5/6] Initialisation Wazuh + SSO Keycloak..."
bash wazuh/init-wazuh.sh
echo "   ✅ Wazuh configuré"

# ── Certificat
echo ""
echo "🔑 [6/6] Certificat CA à installer dans ton navigateur"
echo "   Fichier : $(pwd)/wazuh/certs/root-ca.pem"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  cp wazuh/certs/root-ca.pem /mnt/c/Users/$USER/Desktop/pulse-root-ca.crt 2>/dev/null && \
  echo "   ✅ Copié sur le bureau Windows : pulse-root-ca.crt" || true
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║           ✅ Setup terminé !         ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "🌐 URLs disponibles :"
echo "   https://ai.pulse.local          → Application principale"
echo "   https://auth.pulse.local        → Keycloak (admin SSO)"
echo "   https://wazuh.pulse.local       → Wazuh SIEM (rôle admin)"
echo "   https://grafana.pulse.local     → Grafana"
echo "   https://prometheus.pulse.local  → Prometheus"
echo "   https://traefik.pulse.local     → Traefik dashboard"
echo ""
echo "📋 Comptes de test :"
echo "   admin.technique / Pulse@Admin2026   → Accès complet"
echo "   karim.tazi / (voir .env)            → Rôle RH"
echo ""
echo "📖 Import des données :"
echo "   → https://ai.pulse.local/rh/import"
echo "   → Importer dans l'ordre : departments, jobs, employees (pass1 puis pass2)"
