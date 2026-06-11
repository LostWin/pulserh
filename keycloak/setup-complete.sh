#!/bin/bash
set -e

echo "=== Pulse RH — Configuration Keycloak ==="

/opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 \
  --realm master \
  --client admin-cli \
  --user "$KEYCLOAK_ADMIN" \
  --password "$KEYCLOAK_ADMIN_PASSWORD"

echo "--- Création des utilisateurs ---"

create_user() {
  local USERNAME=$1 PASSWORD=$2 EMAIL=$3 FIRSTNAME=$4 LASTNAME=$5 ROLE=$6
  echo "Creating $USERNAME ($ROLE)..."
  /opt/keycloak/bin/kcadm.sh create users -r pulse \
    -s username="$USERNAME" \
    -s email="$EMAIL" \
    -s firstName="$FIRSTNAME" \
    -s lastName="$LASTNAME" \
    -s enabled=true \
    -s emailVerified=true
  /opt/keycloak/bin/kcadm.sh set-password -r pulse \
    --username "$USERNAME" --new-password "$PASSWORD"
  /opt/keycloak/bin/kcadm.sh add-roles -r pulse \
    --uusername "$USERNAME" --rolename "$ROLE"
  echo "  $USERNAME OK"
}

create_user "youssef.benali"  "Pulse@Collab26"  "youssef.benali@pulse.ma"  "Youssef" "Benali"    "collaborator"
create_user "fatima.alaoui"   "Pulse@Manager26" "fatima.alaoui@pulse.ma"   "Fatima"  "Alaoui"    "manager"
create_user "karim.tazi"      "Pulse@HRteam26"  "karim.tazi@pulse.ma"      "Karim"   "Tazi"      "hr"
create_user "sara.bennani"    "Pulse@Direct26"  "sara.bennani@pulse.ma"    "Sara"    "Bennani"   "director"
create_user "admin.technique" "Pulse@Admin2026" "admin.tech@pulse.ma"      "Admin"   "Technique" "admin"

echo ""
echo "--- Création du client Grafana ---"

/opt/keycloak/bin/kcadm.sh create clients -r pulse \
  -s clientId=grafana \
  -s name="Grafana Dashboard" \
  -s enabled=true \
  -s publicClient=false \
  -s standardFlowEnabled=true \
  -s 'redirectUris=["https://grafana.pulse.local/*"]' \
  -s 'webOrigins=["https://grafana.pulse.local"]' \
  -s protocol=openid-connect \
  -s secret=PulseRH_GrafanaSecret_2026

GRAFANA_ID=$(/opt/keycloak/bin/kcadm.sh get clients -r pulse \
  -q clientId=grafana --fields id | grep '"id"' | cut -d'"' -f4)

echo "  Grafana client ID: $GRAFANA_ID"

# Syntaxe config={} qui fonctionne dans Keycloak 25
/opt/keycloak/bin/kcadm.sh create \
  clients/$GRAFANA_ID/protocol-mappers/models -r pulse \
  -s name="realm-roles-mapper" \
  -s protocol=openid-connect \
  -s protocolMapper=oidc-usermodel-realm-role-mapper \
  -s consentRequired=false \
  -s 'config={"multivalued":"true","userinfo.token.claim":"true","id.token.claim":"true","access.token.claim":"true","claim.name":"roles","jsonType.label":"String"}'

echo "  Roles mapper OK"
echo ""
echo "=== Terminé ==="
echo "collaborator : youssef.benali  / Pulse@Collab26"
echo "manager      : fatima.alaoui   / Pulse@Manager26"
echo "hr           : karim.tazi      / Pulse@HRteam26"
echo "director     : sara.bennani    / Pulse@Direct26"
echo "admin        : admin.technique / Pulse@Admin2026"
