FROM quay.io/keycloak/keycloak:25.0
USER root
COPY themes /opt/keycloak/themes
RUN chown -R keycloak:keycloak /opt/keycloak/themes
USER keycloak
