#!/bin/bash
set -e
echo "=== Setup PulseRH ==="

if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  Copie .env.example → .env — Remplis les variables avant de continuer"
  exit 1
fi

echo "📝 Ajout des entrées /etc/hosts..."
HOSTS="127.0.0.1 ai.pulse.local api.pulse.local auth.pulse.local wazuh.pulse.local grafana.pulse.local prometheus.pulse.local traefik.pulse.local"
grep -q "ai.pulse.local" /etc/hosts || echo "$HOSTS" | sudo tee -a /etc/hosts

echo "🐳 Démarrage des services..."
docker compose up -d

echo "⏳ Attente que les services soient prêts (60s)..."
sleep 60

echo "🗄️  Migrations base de données..."
docker exec pulse_backend bash -c "cd /app && python -m alembic upgrade head"

echo "🔧 Patch audit_logs..."
docker exec pulse_postgres psql -U pulse_ai_user -d pulse_ai \
  -c "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS details JSON;" 2>/dev/null || true

echo "🔐 Initialisation Wazuh..."
bash wazuh/init-wazuh.sh

echo ""
echo "✅ Setup terminé !"
echo ""
echo "📋 Installe le certificat CA dans ton navigateur :"
echo "   wazuh/certs/root-ca.pem"
echo ""
echo "🌐 URLs :"
echo "   https://ai.pulse.local       → Application"
echo "   https://auth.pulse.local     → Keycloak"
echo "   https://wazuh.pulse.local    → Wazuh (rôle admin)"
echo "   https://grafana.pulse.local  → Grafana"
echo "   https://traefik.pulse.local  → Traefik"
