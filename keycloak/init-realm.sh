#!/bin/bash
set -e

echo "[init] Authenticating..."
/opt/keycloak/bin/kcadm.sh config credentials \
  --server http://pulse_keycloak:8080 \
  --realm master \
  --client admin-cli \
  --user "$KEYCLOAK_ADMIN" \
  --password "$KEYCLOAK_ADMIN_PASSWORD"

echo "[init] Checking if realm pulse exists..."
if /opt/keycloak/bin/kcadm.sh get realms/pulse > /dev/null 2>&1; then
  echo "[init] Realm pulse already exists, skipping import."
else
  echo "[init] Importing realm pulse (full config with users)..."
  /opt/keycloak/bin/kcadm.sh create realms \
    -f /opt/keycloak/data/import/realm-export.json
  echo "[init] Realm pulse imported successfully."
fi

echo "[init] Verifying users..."
/opt/keycloak/bin/kcadm.sh get users -r pulse \
  --fields username,enabled 2>/dev/null | grep username || echo "No users found"

echo "[init] Done."
