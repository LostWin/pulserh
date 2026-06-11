#!/bin/bash
set -e

echo ">>> Initialisation des bases Pulse RH..."

create_db_and_user() {
    local DB=$1
    local USER=$2
    local PASSWORD=$3
    echo ">>> Création : $USER / $DB"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE USER ${USER} WITH PASSWORD '${PASSWORD}';
        CREATE DATABASE ${DB}
            WITH OWNER = ${USER}
            ENCODING = 'UTF8'
            LC_COLLATE = 'en_US.utf8'
            LC_CTYPE = 'en_US.utf8'
            TEMPLATE = template0;
        GRANT ALL PRIVILEGES ON DATABASE ${DB} TO ${USER};
        REVOKE ALL ON DATABASE ${DB} FROM PUBLIC;
EOSQL
    echo ">>> OK : $DB"
}

create_db_and_user "${KEYCLOAK_DB}" "${KEYCLOAK_DB_USER}" "${KEYCLOAK_DB_PASSWORD}"
create_db_and_user "${PULSE_AI_DB}" "${PULSE_AI_DB_USER}" "${PULSE_AI_DB_PASSWORD}"
create_db_and_user "${WAZUH_DB}" "${WAZUH_DB_USER}" "${WAZUH_DB_PASSWORD}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    REVOKE ALL ON DATABASE postgres FROM PUBLIC;
EOSQL

echo ">>> Toutes les bases créées avec succès."
