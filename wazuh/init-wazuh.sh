#!/bin/bash
set -e

echo "=== Initialisation Wazuh Security ==="

# Charger les variables d'environnement
source .env

# 1. Attendre que l'indexer soit prêt
echo "⏳ Attente de l'indexer..."
until docker exec wazuh-indexer curl -sk https://localhost:9200 -o /dev/null 2>/dev/null; do
  sleep 5
done
echo "✅ Indexer démarré"

# 2. Générer le hash du mot de passe
echo "🔑 Génération du hash bcrypt..."
HASH=$(docker exec --user root wazuh-indexer bash -c '
  export JAVA_HOME=/usr/share/wazuh-indexer/jdk
  export PATH=$JAVA_HOME/bin:$PATH
  chmod +x /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh
  /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh -p "'"$WAZUH_INDEXER_PASSWORD"'"
' | tail -1)
echo "Hash généré: ${HASH:0:20}..."

# 3. Injecter le hash dans internal_users.yml
echo "📝 Mise à jour du hash admin..."
docker exec --user root wazuh-indexer sed -i \
  "s|hash: .*|hash: \"$HASH\"|" \
  /usr/share/wazuh-indexer/opensearch-security/internal_users.yml

# 4. Copier les fichiers de config corrigés
echo "📁 Injection des configs de sécurité..."
docker cp wazuh/config/opensearch-security-config.yml \
  wazuh-indexer:/usr/share/wazuh-indexer/opensearch-security/config.yml
docker cp wazuh/config/roles_mapping.yml \
  wazuh-indexer:/usr/share/wazuh-indexer/opensearch-security/roles_mapping.yml
docker cp wazuh/config/internal_users.yml \
  wazuh-indexer:/usr/share/wazuh-indexer/opensearch-security/internal_users.yml

# 5. Appliquer la config via securityadmin
echo "🔄 Application de la config OpenSearch Security..."
docker exec --user root wazuh-indexer bash -c '
  export JAVA_HOME=/usr/share/wazuh-indexer/jdk
  export PATH=$JAVA_HOME/bin:$PATH
  chmod +x /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh
  /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh \
    -cd /usr/share/wazuh-indexer/opensearch-security \
    -icl -nhnv \
    -cacert /usr/share/wazuh-indexer/certs/root-ca.pem \
    -cert /usr/share/wazuh-indexer/certs/indexer.pem \
    -key /usr/share/wazuh-indexer/certs/indexer.key \
    -h localhost -p 9200
'
echo "✅ OpenSearch Security configuré"

# 6. Initialiser le client Keycloak wazuh-dashboard
echo "🔐 Configuration du client Keycloak..."
sleep 10

TOKEN=$(curl -sk -X POST \
  "https://auth.pulse.local/realms/master/protocol/openid-connect/token" \
  -d "client_id=admin-cli" \
  -d "username=${KEYCLOAK_ADMIN}" \
  -d "password=${KEYCLOAK_ADMIN_PASSWORD}" \
  -d "grant_type=password" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Vérifier si le client existe déjà
EXISTING=$(curl -sk \
  "https://auth.pulse.local/admin/realms/pulse/clients?clientId=wazuh-dashboard" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if d else '')" 2>/dev/null)

if [ -n "$EXISTING" ]; then
  echo "⚠️  Client wazuh-dashboard existe déjà, suppression..."
  curl -sk -X DELETE \
    "https://auth.pulse.local/admin/realms/pulse/clients/$EXISTING" \
    -H "Authorization: Bearer $TOKEN" > /dev/null
fi

# Créer le client
CLIENT_ID=$(curl -sk -X POST \
  "https://auth.pulse.local/admin/realms/pulse/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "wazuh-dashboard",
    "name": "Wazuh Dashboard",
    "enabled": true,
    "protocol": "openid-connect",
    "publicClient": false,
    "secret": "'"$WAZUH_DASHBOARD_CLIENT_SECRET"'",
    "redirectUris": ["https://wazuh.pulse.local/*"],
    "webOrigins": ["https://wazuh.pulse.local"],
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": true,
    "fullScopeAllowed": true,
    "authorizationServicesEnabled": true,
    "serviceAccountsEnabled": true,
    "attributes": {
      "post.logout.redirect.uris": "https://wazuh.pulse.local/*"
    }
  }' -w "%{http_code}" -o /dev/null)

TOKEN=$(curl -sk -X POST \
  "https://auth.pulse.local/realms/master/protocol/openid-connect/token" \
  -d "client_id=admin-cli" \
  -d "username=${KEYCLOAK_ADMIN}" \
  -d "password=${KEYCLOAK_ADMIN_PASSWORD}" \
  -d "grant_type=password" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

CLIENT_UUID=$(curl -sk \
  "https://auth.pulse.local/admin/realms/pulse/clients?clientId=wazuh-dashboard" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

# Ajouter le mapper de rôles
curl -sk -X POST \
  "https://auth.pulse.local/admin/realms/pulse/clients/$CLIENT_UUID/protocol-mappers/models" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "realm-roles-mapper",
    "protocol": "openid-connect",
    "protocolMapper": "oidc-usermodel-realm-role-mapper",
    "consentRequired": false,
    "config": {
      "claim.name": "roles",
      "jsonType.label": "String",
      "multivalued": "true",
      "userinfo.token.claim": "true",
      "id.token.claim": "true",
      "access.token.claim": "true",
      "introspection.token.claim": "true"
    }
  }' > /dev/null

echo "✅ Client Keycloak configuré"
echo ""
echo "🎉 Initialisation Wazuh terminée !"
echo "   → https://wazuh.pulse.local"
echo "   → Connexion avec un utilisateur ayant le rôle 'admin'"
