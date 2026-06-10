#!/usr/bin/env python3
"""Génère un README.md complet pour le projet Pulse RH Security."""

README_CONTENT = """\
# 🛡️ Pulse RH – Infrastructure Sécurité & SSO

**Plateforme RH augmentée par l'IA**
Projet Y‑Days 2026 – Ynov Campus Maroc
**Version 1.0**

---

## 📦 Contenu du dépôt

- **Stack complète** Docker Compose : Traefik, Keycloak, PostgreSQL, Redis, Prometheus, Grafana, Wazuh
- **Authentification unique (SSO)** via Keycloak pour Grafana et Wazuh
- **5 rôles métiers** : `collaborator`, `manager`, `hr`, `director`, `admin`
- **Règles de sécurité personnalisées** pour Wazuh (brute force, prompt injection, RBAC, etc.)
- **Documentation d'intégration** pour les équipes backend et frontend

---

## 🏗️ Architecture (vue textuelle)

```
Internet (HTTPS)
│
▼
┌─────────────────────────────────┐
│         Traefik v3.1            │
│   Reverse proxy + TLS           │
│   (traefik.pulse.local)         │
└───────┬─────────────┬───────────┘
        │             │
        ▼             ▼
┌──────────────┐  ┌──────────────────────────────┐
│   Keycloak   │  │     Services applicatifs      │
│  OIDC / SAML │  │                               │
│  Port 8080   │  │  Grafana        (port 3000)   │
│  (interne)   │  │  Wazuh Dashboard(port 5601)   │
└──────┬───────┘  │  Prometheus     (port 9090)   │
       │          └──────────────────────────────┘
       │                        │
       ▼                        ▼
┌──────────────┐  ┌───────────────────────────┐
│  PostgreSQL  │  │ Wazuh Indexer (OpenSearch)│
│  (multi-BDD) │  │ Wazuh Manager             │
└──────────────┘  │ (règles + logs)           │
                  └───────────────────────────┘
```

---

## 🚀 Démarrage rapide

### Prérequis

- **Docker** ≥ 24.0 et **Docker Compose** v2
- **Git**
- **Accès administrateur** (pour modifier `/etc/hosts`)
- **WSL2 / Linux / macOS** (les volumes utilisent des chemins Unix)

### 1. Cloner le dépôt

```bash
git clone https://github.com/<votre-compte>/pulse-rh-security.git
cd pulse-rh-security
```

### 2. Configurer les noms de domaine locaux

```bash
sudo ./setup-hosts.sh
```

ou ajouter manuellement dans `/etc/hosts` :

```
127.0.0.1 auth.pulse.local
127.0.0.1 traefik.pulse.local
127.0.0.1 prometheus.pulse.local
127.0.0.1 grafana.pulse.local
127.0.0.1 wazuh.pulse.local
```

### 3. Fichier d'environnement

```bash
cp .env.example .env
# Éditer .env si nécessaire (mots de passe, etc.)
```

### 4. Lancer la stack

```bash
docker compose up -d
```

> Attendre que tous les services soient **healthy** (vérifier avec `docker compose ps`).
> Le premier démarrage peut prendre quelques minutes (téléchargement des images, initialisation).

### 5. Accéder aux services

| Service             | URL                              | Identifiants / Authentification                        |
|---------------------|----------------------------------|--------------------------------------------------------|
| Traefik Dashboard   | https://traefik.pulse.local      | Basic Auth (voir `.env`)                              |
| Keycloak Admin      | https://auth.pulse.local/admin   | `admin` / `PulseRH_AdminKC_2026Secure`                |
| Prometheus          | https://prometheus.pulse.local   | aucune                                                 |
| Grafana             | https://grafana.pulse.local      | SSO Keycloak (bouton "Log in with Keycloak")          |
| Wazuh Dashboard     | https://wazuh.pulse.local        | SSO Keycloak (redirection automatique)                |

> **Note :** Les certificats sont auto‑signés, votre navigateur affichera un avertissement. Acceptez‑le.

---

## 👥 Comptes de test Keycloak

| Utilisateur        | Rôle          | Mot de passe        |
|--------------------|---------------|---------------------|
| youssef.benali     | collaborator  | `Pulse@Collab26`    |
| fatima.alaoui      | manager       | `Pulse@Manager26`   |
| karim.tazi         | hr            | `Pulse@HRteam26`    |
| sara.bennani       | director      | `Pulse@Direct26`    |
| admin.technique    | admin         | `Pulse@Admin2026`   |

---

## 🔐 Configuration Keycloak

- **Realm** : `pulse`
- **Clients OIDC déjà enregistrés** :
  - `grafana` (secret : `PulseRH_GrafanaSecret_2026`)
  - `wazuh-dashboard` (secret : `PulseRH_WazuhDash_Secret2026`)
  - `pulse-web` (pour le frontend, à configurer)
  - `pulse-backend` (pour l'API, à configurer)
- **Rôles** : `collaborator`, `manager`, `hr`, `director`, `admin`

---

## 📁 Structure du projet

```
pulse-rh-security/
├── docker-compose.yml           # Stack Docker Compose complète
├── .env.example                 # Modèle de variables d'environnement
├── setup-hosts.sh               # Ajoute les domaines locaux dans /etc/hosts
├── generate_readme.py           # Ce script Python pour générer le README
├── README.md
├── traefik/
│   ├── traefik.yml
│   ├── dynamic/
│   │   ├── routes.yml
│   │   └── middleware.yml
│   └── certs/                   # Certificats TLS (pulse.crt, pulse.key)
├── keycloak/
│   ├── realm-export.json        # Export complet du realm pulse
│   └── init-realm.sh
├── grafana/
│   └── grafana.ini              # Configuration Grafana + OIDC
├── prometheus/
│   └── prometheus.yml
├── wazuh/
│   ├── config/
│   │   ├── wazuh-indexer.yml
│   │   ├── wazuh-dashboard.yml
│   │   └── ossec-minimal.conf   # Optionnel (non monté par défaut)
│   ├── certs/                   # Certificats internes Wazuh
│   └── rules/
│       └── pulse_rules.xml      # Règles de sécurité personnalisées
├── redis/
│   └── redis.conf
└── postgres/
    └── init.sh                  # Crée les bases de données au démarrage
```

---

## 🔧 Intégration backend (FastAPI)

### 1. Validation du token JWT

Le backend doit valider le token JWT émis par Keycloak.

- Récupérer la clé publique :
  ```
  GET https://auth.pulse.local/realms/pulse/protocol/openid-connect/certs
  ```
- Utiliser `python-jose` ou `PyJWT` pour décoder et vérifier le token.
- Vérifier : signature, expiration (`exp`), audience (`pulse-backend`), issuer (`https://auth.pulse.local/realms/pulse`).

**Exemple de code (FastAPI) :**

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import requests

KEYCLOAK_CERTS_URL = "https://auth.pulse.local/realms/pulse/protocol/openid-connect/certs"
ALGORITHMS = ["RS256"]

def get_public_keys():
    return requests.get(KEYCLOAK_CERTS_URL, verify=False).json()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
):
    token = credentials.credentials
    jwks = get_public_keys()
    payload = jwt.decode(
        token,
        jwks,
        algorithms=ALGORITHMS,
        audience="pulse-backend",
        issuer="https://auth.pulse.local/realms/pulse",
    )
    return payload

@app.get("/secure")
async def secure_endpoint(user=Depends(get_current_user)):
    roles = user.get("realm_access", {}).get("roles", [])
    if "admin" not in roles:
        raise HTTPException(403, "Accès refusé")
    return {"message": "Bienvenue admin"}
```

### 2. Extraction des rôles

Les rôles du realm sont dans `realm_access.roles` :

```json
{
  "realm_access": {
    "roles": ["collaborator", "manager"]
  }
}
```

Utilisez ces rôles pour implémenter le RBAC (contrôle d'accès basé sur les rôles).

### 3. Format des logs de sécurité pour Wazuh

Le backend doit envoyer les événements de sécurité au format JSON vers le port UDP 514 du manager Wazuh (`wazuh-manager`).

**Exemple de log JSON :**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "user_id": "6d5cfe65-...",
  "role": "collaborator",
  "action": "chat_request",
  "endpoint": "/chat",
  "status": "REFUSED",
  "reason": "prompt_injection_detected",
  "ip": "192.168.1.1"
}
```

**Implémentation Python (syslog) :**

```python
import logging
import logging.handlers
import socket
import json

logger = logging.getLogger("pulse_security")
handler = logging.handlers.SysLogHandler(
    address=("wazuh-manager", 514),
    socktype=socket.SOCK_DGRAM,
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_event(event_dict: dict):
    logger.info(json.dumps(event_dict))
```

**Les règles Wazuh correspondantes** (dans `pulse_rules.xml`) déclenchent des alertes :

- ID `100020` : prompt injection détectée
- ID `100010` : accès hors périmètre RBAC
- ID `100002` : brute force (5 échecs en 2 min)

---

## 🎨 Intégration frontend (React)

### 1. Installation

```bash
npm install keycloak-js
```

### 2. Configuration du client Keycloak

```tsx
import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: "https://auth.pulse.local",
  realm: "pulse",
  clientId: "pulse-web",
});

keycloak
  .init({
    onLoad: "login-required",
    pkceMethod: "S256",
    checkLoginIframe: false,
  })
  .then((authenticated) => {
    if (authenticated) {
      console.log("Authentifié");
      localStorage.setItem("token", keycloak.token);
    }
  });
```

### 3. Ajout du token aux requêtes API

```tsx
const token = keycloak.token;
fetch("https://api.pulse.local/data", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

### 4. Redirection selon le rôle

```tsx
const roles = keycloak.tokenParsed?.realm_access?.roles || [];
if (roles.includes("admin")) {
  window.location.href = "/admin";
} else if (roles.includes("manager")) {
  window.location.href = "/manager";
}
```

---

## 🛠️ Maintenance & dépannage

- **Vérifier l'état des services** : `docker compose ps`
- **Afficher les logs** : `docker compose logs -f <service>`
- **Bad Gateway** : Vérifier que le conteneur concerné est `healthy`. Si le problème persiste, redémarrer : `docker compose restart <service>`
- **Erreur 401 Unauthorized sur Wazuh** : `docker compose restart wazuh-indexer`
- **Réinitialiser complètement Wazuh** (⚠️ perte des données) :

```bash
docker compose down wazuh-indexer wazuh-manager wazuh-dashboard
docker volume rm pulse-rh_wazuh_indexer_data pulse-rh_wazuh_manager_data
docker compose up -d
```

---

## 📜 Licence

Projet interne Ynov Campus Maroc – Y‑Days 2026.

---

*README généré automatiquement par `generate_readme.py`*
"""


def main():
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(README_CONTENT)
    print("✅ README.md généré avec succès.")


if __name__ == "__main__":
    main()