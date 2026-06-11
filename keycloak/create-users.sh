#!/bin/bash
set -e

echo "[users] Authenticating..."
/opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 \
  --realm master \
  --client admin-cli \
  --user "$KEYCLOAK_ADMIN" \
  --password "$KEYCLOAK_ADMIN_PASSWORD"

echo "[users] Creating test users..."

create_user() {
  USERNAME=$1
  PASSWORD=$2
  EMAIL=$3
  FIRSTNAME=$4
  LASTNAME=$5
  ROLE=$6

  echo "[users] Creating $USERNAME ($ROLE)..."

  /opt/keycloak/bin/kcadm.sh create users -r pulse \
    -s username="$USERNAME" \
    -s email="$EMAIL" \
    -s firstName="$FIRSTNAME" \
    -s lastName="$LASTNAME" \
    -s enabled=true \
    -s emailVerified=true

  /opt/keycloak/bin/kcadm.sh set-password -r pulse \
    --username "$USERNAME" \
    --new-password "$PASSWORD"

  /opt/keycloak/bin/kcadm.sh add-roles -r pulse \
    --uusername "$USERNAME" \
    --rolename "$ROLE"

  echo "[users] $USERNAME created with role $ROLE ✓"
}

# Collaborateur
create_user "youssef.benali" "Test@Collab2026" "youssef.benali@pulse.ma" "Youssef" "Benali" "collaborator"

# Manager
create_user "fatima.alaoui" "Test@Manager2026" "fatima.alaoui@pulse.ma" "Fatima" "Alaoui" "manager"

# RH
create_user "karim.tazi" "Test@HR2026" "karim.tazi@pulse.ma" "Karim" "Tazi" "hr"

# Directeur
create_user "sara.bennani" "Test@Director2026" "sara.bennani@pulse.ma" "Sara" "Bennani" "director"

# Admin technique
create_user "admin.technique" "Test@Admin2026" "admin.technique@pulse.ma" "Admin" "Technique" "admin"

echo ""
echo "[users] All users created successfully!"
echo ""
echo "Credentials summary:"
echo "  collaborator : youssef.benali    / Test@Collab2026"
echo "  manager      : fatima.alaoui     / Test@Manager2026"
echo "  hr           : karim.tazi        / Test@HR2026"
echo "  director     : sara.bennani      / Test@Director2026"
echo "  admin        : admin.technique   / Test@Admin2026"
