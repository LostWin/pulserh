import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: import.meta.env.VITE_KEYCLOAK_URL || 'https://auth.pulse.local',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'pulse',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT || 'pulse-web'
});

export default keycloak;
