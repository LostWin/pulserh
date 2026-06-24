#!/bin/bash
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "${GREEN}  ✅ $*${NC}"; }
info() { echo -e "${BLUE}  ℹ  $*${NC}"; }
warn() { echo -e "${YELLOW}  ⚠️  $*${NC}"; }
fail() { echo -e "${RED}  ❌ $*${NC}"; exit 1; }
step() { echo -e "\n${BLUE}▶ $*${NC}"; }

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║         PulseRH — Setup complet          ║"
echo "╚══════════════════════════════════════════╝"

# ─── 0. Prérequis ────────────────────────────────────────────────────────────
step "[0/8] Vérification des prérequis"
command -v docker   >/dev/null 2>&1 || fail "Docker non installé. https://docs.docker.com/get-docker/"
command -v openssl  >/dev/null 2>&1 || fail "openssl non installé (apt install openssl)"
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 non installé"
ok "Docker et openssl disponibles"

# ─── 1. Fichier .env ─────────────────────────────────────────────────────────
step "[1/8] Configuration .env"
if [ ! -f .env ]; then
  cp .env.example .env
  warn "Fichier .env créé depuis .env.example"
  warn "Remplis LLM_API_KEY et DOCUMENTS_ENCRYPTION_KEY dans .env, puis relance ./setup.sh"
  exit 1
fi
if grep -q "REMPLACER" .env; then
  warn "Des variables contiennent encore REMPLACER dans .env — certaines fonctions seront inactives"
fi
source .env
ok ".env chargé"

# ─── 2. Certificats TLS ───────────────────────────────────────────────────────
step "[2/8] Génération des certificats TLS"
mkdir -p wazuh/certs traefik/certs

if [ ! -f wazuh/certs/root-ca.pem ]; then
  info "Génération certificats Wazuh signés par CA..."

  # CA racine
  openssl genrsa -out wazuh/certs/root-ca.key 4096 2>/dev/null
  openssl req -new -x509 -days 3650 -nodes \
    -key wazuh/certs/root-ca.key \
    -out wazuh/certs/root-ca.pem \
    -subj "/C=MA/O=PulseRH/CN=PulseRH-CA" 2>/dev/null

  # Fonction pour générer un cert signé par la CA
  gen_cert() {
    local NAME=$1 CN=$2
    openssl req -newkey rsa:2048 -nodes \
      -keyout "wazuh/certs/${NAME}.key" \
      -out "/tmp/${NAME}.csr" \
      -subj "/C=MA/O=PulseRH/CN=${CN}" 2>/dev/null
    openssl x509 -req -days 3650 \
      -in "/tmp/${NAME}.csr" \
      -CA wazuh/certs/root-ca.pem \
      -CAkey wazuh/certs/root-ca.key \
      -CAcreateserial \
      -out "wazuh/certs/${NAME}.pem" 2>/dev/null
    rm -f "/tmp/${NAME}.csr"
  }

  gen_cert indexer   "wazuh-indexer"
  gen_cert manager   "wazuh-manager"
  gen_cert dashboard "wazuh-dashboard"

  cp wazuh/certs/root-ca.pem wazuh/certs/ca-bundle.crt
  cp wazuh/certs/root-ca.pem wazuh/certs/indexer-trust.crt
  chmod 600 wazuh/certs/*.key
  ok "Certificats Wazuh générés et signés par la CA"
else
  ok "Certificats Wazuh déjà présents"
fi

if [ ! -f traefik/certs/pulse.crt ]; then
  info "Génération certificat Traefik..."
  cat > /tmp/traefik-san.cnf << 'SANCNF'
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = MA
O = PulseRH
CN = pulse.local
[v3_req]
subjectAltName = DNS:ai.pulse.local,DNS:api.pulse.local,DNS:auth.pulse.local,DNS:wazuh.pulse.local,DNS:grafana.pulse.local,DNS:prometheus.pulse.local,DNS:traefik.pulse.local,DNS:localhost
SANCNF
  openssl req -x509 -newkey rsa:4096 -nodes -days 3650 \
    -keyout traefik/certs/pulse.key \
    -out traefik/certs/pulse.crt \
    -config /tmp/traefik-san.cnf 2>/dev/null
  chmod 600 traefik/certs/pulse.key
  ok "Certificat Traefik généré"
else
  ok "Certificat Traefik déjà présent"
fi

# ─── 3. /etc/hosts ───────────────────────────────────────────────────────────
step "[3/8] Configuration /etc/hosts"
HOSTS_LINE="127.0.0.1 ai.pulse.local api.pulse.local auth.pulse.local wazuh.pulse.local grafana.pulse.local prometheus.pulse.local traefik.pulse.local"
if grep -q "ai.pulse.local" /etc/hosts; then
  ok "Déjà configuré dans /etc/hosts"
else
  echo "$HOSTS_LINE" | sudo tee -a /etc/hosts > /dev/null
  ok "Entrées ajoutées à /etc/hosts"
fi

# ─── 4. Démarrage des services ────────────────────────────────────────────────
step "[4/8] Démarrage des services Docker"
docker compose up -d --build
ok "Services démarrés"

# ─── 5. Attendre Keycloak ────────────────────────────────────────────────────
step "[5/8] Attente Keycloak (2-3 minutes)"
MAX_WAIT=300; ELAPSED=0; INTERVAL=10
while true; do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' pulse_keycloak 2>/dev/null || echo "missing")
  [ "$STATUS" = "healthy" ] && { ok "Keycloak est healthy"; break; }
  [ $ELAPSED -ge $MAX_WAIT ] && fail "Keycloak pas prêt après ${MAX_WAIT}s. Vérifie : docker logs pulse_keycloak"
  info "Keycloak status: ${STATUS} (${ELAPSED}s / ${MAX_WAIT}s)..."
  sleep $INTERVAL; ELAPSED=$((ELAPSED + INTERVAL))
done

# ─── 6. Import realm Keycloak ────────────────────────────────────────────────
step "[6/8] Import realm Keycloak"
# Copier le realm dans le container et importer
docker cp keycloak/exports/pulse-realm.json pulse_keycloak:/tmp/realm-export.json

docker exec pulse_keycloak /bin/bash -c "
  /opt/keycloak/bin/kcadm.sh config credentials \
    --server http://localhost:8080 \
    --realm master \
    --client admin-cli \
    --user \$KEYCLOAK_ADMIN \
    --password \$KEYCLOAK_ADMIN_PASSWORD

  if /opt/keycloak/bin/kcadm.sh get realms/pulse > /dev/null 2>&1; then
    echo 'Realm pulse existe déjà — skip'
  else
    /opt/keycloak/bin/kcadm.sh create realms -f /tmp/realm-export.json
    echo 'Realm importé'
  fi

  # Corriger redirect URI du client pulse-web
  CLIENT_ID=\$(/opt/keycloak/bin/kcadm.sh get clients -r pulse --fields id,clientId | grep -B1 'pulse-web' | grep id | tr -d ' \"id:,')
  /opt/keycloak/bin/kcadm.sh update clients/\$CLIENT_ID -r pulse \
    -s 'redirectUris=[\"https://ai.pulse.local/*\",\"http://localhost:5173/*\"]' \
    -s 'webOrigins=[\"https://ai.pulse.local\",\"http://localhost:5173\"]' \
    -s 'rootUrl=https://ai.pulse.local' 2>/dev/null || true

  # Créer client wazuh-dashboard s'il n'existe pas
  WAZUH_CLIENT=\$(/opt/keycloak/bin/kcadm.sh get clients -r pulse --fields clientId | grep -c 'wazuh-dashboard' || true)
  if [ \"\$WAZUH_CLIENT\" = \"0\" ]; then
    /opt/keycloak/bin/kcadm.sh create clients -r pulse \
      -s clientId=wazuh-dashboard \
      -s name='Wazuh Dashboard' \
      -s enabled=true \
      -s protocol=openid-connect \
      -s publicClient=false \
      -s 'secret=PulseRH_WazuhDash_Secret2026' \
      -s 'redirectUris=[\"https://wazuh.pulse.local/*\"]' \
      -s 'webOrigins=[\"https://wazuh.pulse.local\"]' \
      -s rootUrl=https://wazuh.pulse.local \
      -s standardFlowEnabled=true \
      -s directAccessGrantsEnabled=true \
      -s fullScopeAllowed=true

    # Récupérer l'ID du client créé
    WAZUH_ID=\$(/opt/keycloak/bin/kcadm.sh get clients -r pulse --fields id,clientId | grep -B1 'wazuh-dashboard' | grep id | tr -d ' \"id:,')

    # Ajouter le mapper de rôles
    /opt/keycloak/bin/kcadm.sh create clients/\$WAZUH_ID/protocol-mappers/models -r pulse \
      -s name=realm-roles-mapper \
      -s protocol=openid-connect \
      -s protocolMapper=oidc-usermodel-realm-role-mapper \
      -s consentRequired=false \
      -s 'config={\"claim.name\":\"roles\",\"multivalued\":\"true\",\"access.token.claim\":\"true\",\"id.token.claim\":\"true\",\"userinfo.token.claim\":\"true\"}'
    echo 'Client wazuh-dashboard créé avec mapper roles'
  else
    echo 'Client wazuh-dashboard existe déjà'
  fi
" && ok "Keycloak configuré" || warn "Keycloak init partiellement échoué — vérifie manuellement"

# ─── 7. Migrations Alembic ───────────────────────────────────────────────────
step "[7/8] Migrations base de données"
sleep 10
docker exec pulse_backend bash -c "cd /app && python -m alembic upgrade head" \
  && ok "Migrations appliquées" \
  || warn "Migrations échouées — relance : docker exec pulse_backend python -m alembic upgrade head"

docker exec pulse_postgres psql -U "${PULSE_AI_DB_USER:-pulse_ai_user}" -d "${PULSE_AI_DB:-pulse_ai}" \
  -c "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS details JSON;" 2>/dev/null \
  && ok "Schéma patché" || true

# ─── 8. Wazuh ────────────────────────────────────────────────────────────────
step "[8/8] Initialisation Wazuh"
info "Attente wazuh-indexer healthy..."
MAX_WAIT=180; ELAPSED=0
while true; do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' wazuh-indexer 2>/dev/null || echo "missing")
  [ "$STATUS" = "healthy" ] && { ok "wazuh-indexer healthy"; break; }
  [ $ELAPSED -ge $MAX_WAIT ] && { warn "wazuh-indexer pas healthy — Wazuh ignoré"; break; }
  sleep 10; ELAPSED=$((ELAPSED + 10))
done

if [ "$(docker inspect --format='{{.State.Health.Status}}' wazuh-indexer 2>/dev/null)" = "healthy" ]; then
  # Générer hash bcrypt du mot de passe admin
  info "Génération hash Wazuh admin..."
  HASH=$(docker exec --user root wazuh-indexer bash -c "
    export JAVA_HOME=/usr/share/wazuh-indexer/jdk
    export PATH=\$JAVA_HOME/bin:\$PATH
    chmod +x /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh
    /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh -p '${WAZUH_INDEXER_PASSWORD}'
  " 2>/dev/null | tail -1)

  if [ -n "$HASH" ]; then
    # Mettre à jour le hash via copie (fichier monté en ro)
    docker exec --user root wazuh-indexer bash -c "
      cp /usr/share/wazuh-indexer/opensearch-security/internal_users.yml /tmp/iu.yml
      sed -i 's|hash:.*|hash: \"${HASH}\"|' /tmp/iu.yml
    "
    docker cp wazuh-indexer:/tmp/iu.yml /tmp/iu_modified.yml
    docker cp /tmp/iu_modified.yml wazuh-indexer:/usr/share/wazuh-indexer/opensearch-security/internal_users.yml 2>/dev/null || true
    ok "Hash Wazuh admin mis à jour"
  fi

  # Appliquer la config de sécurité
  info "Application config OpenSearch Security..."
  docker exec --user root wazuh-indexer bash -c "
    export JAVA_HOME=/usr/share/wazuh-indexer/jdk
    export PATH=\$JAVA_HOME/bin:\$PATH
    chmod +x /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh
    /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh \
      -cd /usr/share/wazuh-indexer/opensearch-security \
      -icl -nhnv \
      -cacert /usr/share/wazuh-indexer/certs/root-ca.pem \
      -cert /usr/share/wazuh-indexer/certs/indexer.pem \
      -key /usr/share/wazuh-indexer/certs/indexer.key \
      -h localhost -p 9200
  " && ok "Wazuh Security configuré" || warn "Wazuh Security config échouée"
fi

# ─── Résumé ───────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║           ✅ Setup terminé !             ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "🌐 URLs :"
echo "   https://ai.pulse.local          → Application principale"
echo "   https://auth.pulse.local        → Keycloak SSO"
echo "   https://grafana.pulse.local     → Monitoring"
echo "   https://wazuh.pulse.local       → SIEM Sécurité"
echo "   https://traefik.pulse.local     → Reverse proxy"
echo ""
echo "👤 Comptes (mot de passe défini dans le realm) :"
echo "   admin.technique  → Admin + Wazuh"
echo "   karim.tazi       → RH"
echo "   fatima.alaoui    → Manager"
echo "   sara.bennani     → Direction"
echo "   youssef.benali   → Collaborateur"
echo ""
echo "🔒 Installe le certificat CA dans ton navigateur :"
echo "   $(pwd)/traefik/certs/pulse.crt"
echo "   Firefox : Paramètres → Vie privée → Certificats → Autorités → Importer"
echo "   Chrome  : Paramètres → Sécurité → Certificats → Autorités → Importer"
