#!/bin/bash
set -e

KC_URL="http://pulse_keycloak:8080"

echo "[init] Attente que Keycloak soit prêt..."
until curl -sf "${KC_URL}/health/ready" > /dev/null 2>&1; do
  echo "[init]   ... pas encore prêt, on attend 5s"
  sleep 5
done
echo "[init] Keycloak est prêt."

echo "[init] Authentification admin..."
/opt/keycloak/bin/kcadm.sh config credentials \
  --server "${KC_URL}" \
  --realm master \
  --client admin-cli \
  --user "$KEYCLOAK_ADMIN" \
  --password "$KEYCLOAK_ADMIN_PASSWORD"

echo "[init] Vérification du realm pulse..."
if /opt/keycloak/bin/kcadm.sh get realms/pulse > /dev/null 2>&1; then
  echo "[init] Realm pulse existe déjà — skip import."
else
  echo "[init] Import du realm pulse..."
  /opt/keycloak/bin/kcadm.sh create realms \
    -f /opt/keycloak/data/import/realm-export.json
  echo "[init] Realm importé avec succès."
fi

echo "[init] Application du thème de login..."
/opt/keycloak/bin/kcadm.sh update realms/pulse -s loginTheme=keycloak || true

echo "[init] Vérification des utilisateurs..."
/opt/keycloak/bin/kcadm.sh get users -r pulse \
  --fields username,enabled 2>/dev/null | grep username || echo "[init] Aucun user trouvé"

echo "[init] Initialisation terminée avec succès."
