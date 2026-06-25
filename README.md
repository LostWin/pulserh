# PulseRH — Plateforme RH augmentée par l'IA

> Plateforme RH de nouvelle génération combinant intelligence artificielle, automatisation des processus RH et sécurité de niveau entreprise.
> Projet Y-Days 2026 — Ynov Campus Maroc

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Prérequis](#prérequis)
4. [Installation rapide](#installation-rapide)
5. [Configuration](#configuration)
6. [Comptes de test](#comptes-de-test)
7. [URLs des services](#urls-des-services)
8. [Installer le certificat TLS](#installer-le-certificat-tls)
9. [Structure du projet](#structure-du-projet)
10. [Fonctionnalités par rôle](#fonctionnalités-par-rôle)
11. [Commandes utiles](#commandes-utiles)
12. [Dépannage](#dépannage)
13. [Architecture technique détaillée](#architecture-technique-détaillée)

---

## Vue d'ensemble

PulseRH est une plateforme RH complète qui intègre :

- **Assistant IA** (RAG + LLM) pour les questions RH, l'analyse de documents et la génération de rapports
- **Gestion RH complète** : employés, congés, formations, compétences, entretiens, onboarding
- **Tableau de bord analytique** avec prédictions de turnover et insights talents
- **SSO centralisé** via Keycloak avec 5 rôles métiers
- **Monitoring** Prometheus + Grafana
- **SIEM** Wazuh pour la détection d'intrusion et la sécurité

---

## Architecture

```
Internet (HTTPS)
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                    Traefik v3.1                            │
│         Reverse Proxy + TLS termination                   │
│   ai.pulse.local  api.pulse.local  auth.pulse.local       │
│   wazuh.pulse.local  grafana.pulse.local                  │
└──────┬────────────────┬───────────────────┬───────────────┘
       │                │                   │
       ▼                ▼                   ▼
┌────────────┐  ┌───────────────┐  ┌────────────────────┐
│  Frontend  │  │  Backend API  │  │  Services Sécurité │
│ React/Vite │  │   FastAPI     │  │                    │
│   nginx    │  │   + RAG/LLM   │  │  Keycloak (SSO)    │
└────────────┘  └───────┬───────┘  │  Wazuh (SIEM)      │
                        │          │  Prometheus+Grafana │
                        ▼          └────────────────────┘
             ┌─────────────────┐
             │   Data Layer    │
             │  PostgreSQL     │
             │  Redis (cache)  │
             │  Qdrant (vecs)  │
             │  MinIO (S3)     │
             └─────────────────┘
```

### Réseaux Docker

| Réseau | Description |
|--------|-------------|
| `pulse_public` | Services accessibles via Traefik (frontend, backend, keycloak, wazuh) |
| `pulse_internal` | Services internes uniquement (prometheus, redis, exporters) |
| `pulse_data` | Bases de données isolées (postgres, redis, minio, qdrant) |

---

## Prérequis

| Outil | Version minimale | Installation |
|-------|-----------------|--------------|
| Docker | 24+ | https://docs.docker.com/get-docker/ |
| Docker Compose | v2 (plugin) | Inclus dans Docker Desktop |
| openssl | n'importe | `sudo apt install openssl` |
| Git | n'importe | `sudo apt install git` |

**RAM recommandée** : 8 Go minimum (Wazuh consomme ~2-3 Go à lui seul)  
**Espace disque** : 20 Go minimum

---

## Installation rapide

### Étape 1 — Cloner le repo

```bash
git clone https://github.com/LostWin/pulserh.git
cd pulserh
git checkout dev
```

### Étape 2 — Configurer les variables d'environnement

```bash
# Copier le fichier exemple
cp .env.example .env
```

Ouvre `.env` et renseigne les deux valeurs obligatoires :

```bash
# Clé API OpenRouter (https://openrouter.ai/keys)
LLM_API_KEY=sk-or-v1-REMPLACER_PAR_TA_CLE

# Clé de chiffrement des documents (générer avec la commande ci-dessous)
DOCUMENTS_ENCRYPTION_KEY=$(openssl rand -hex 32)
```

Toutes les autres valeurs ont des valeurs par défaut fonctionnelles.

### Étape 3 — Lancer le setup

```bash
chmod +x setup.sh
./setup.sh
```

Le script fait tout automatiquement :
- Génère les certificats TLS (Traefik + Wazuh)
- Configure `/etc/hosts` avec les domaines `.pulse.local`
- Démarre tous les services Docker
- Attend que Keycloak soit prêt
- Importe le realm Keycloak avec les utilisateurs et clients
- Lance les migrations de base de données
- Configure Wazuh (hash mot de passe admin + securityadmin)

**Durée estimée** : 3 à 8 minutes selon la machine.

### Étape 4 — Installer le certificat dans le navigateur

Pour que HTTPS fonctionne sans avertissement, installe le certificat CA généré par le setup.

Le fichier est à : `traefik/certs/pulse.crt`

**Firefox :**
```
Paramètres → Vie privée et sécurité → Afficher les certificats
→ Autorités → Importer → sélectionne traefik/certs/pulse.crt
→ Cocher "Faire confiance pour identifier les sites web" → OK
```

**Chrome / Edge (Linux) :**
```
Paramètres → Sécurité → Gérer les certificats
→ Autorités → Importer → sélectionne traefik/certs/pulse.crt
→ Faire confiance pour les sites web → OK
```

**Chrome / Edge (Windows) :**
```
Double-clic sur traefik/certs/pulse.crt
→ Installer le certificat → Machine locale
→ Placer dans : Autorités de certification racines de confiance → Terminer
```

**macOS :**
```
Double-clic sur traefik/certs/pulse.crt → Trousseau d'accès
→ Trouver "pulse.local" → Double-clic → Faire confiance → Toujours faire confiance
```

### Étape 5 — Configurer le Client-WEB
```
docker exec -it pulse_keycloak bash -c '
/opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 \
  --realm master \
  --client admin-cli \
  --user $KEYCLOAK_ADMIN \
  --password $KEYCLOAK_ADMIN_PASSWORD

CLIENT_ID=$(
  /opt/keycloak/bin/kcadm.sh get clients -r pulse --fields id,clientId |
  grep -B1 "\"clientId\" : \"pulse-web\"" |
  grep "\"id\"" |
  sed -E "s/.*\"id\" : \"([^\"]+)\".*/\1/"
)

echo "Client ID trouvé : $CLIENT_ID"

/opt/keycloak/bin/kcadm.sh update clients/$CLIENT_ID -r pulse \
  -s '\''rootUrl=https://ai.pulse.local'\'' \
  -s '\''redirectUris=["https://ai.pulse.local/*","http://localhost:5173/*"]'\'' \
  -s '\''webOrigins=["https://ai.pulse.local","http://localhost:5173"]'\''

echo "✅ pulse-web mis à jour"
'
```

### Étape 6 — Créer le role-mapping

```
docker exec -it pulse_keycloak /bin/bash -c "
  /opt/keycloak/bin/kcadm.sh config credentials \
    --server http://localhost:8080 \
    --realm master \
    --client admin-cli \
    --user \$KEYCLOAK_ADMIN \
    --password \$KEYCLOAK_ADMIN_PASSWORD

  CLIENT_UUID=\$(/opt/keycloak/bin/kcadm.sh get clients -r pulse -q clientId=wazuh-dashboard | grep '\"id\"' | head -1 | cut -d '\"' -f4)

  echo \"Client UUID: \$CLIENT_UUID\"

  MAPPER_ID=\$(/opt/keycloak/bin/kcadm.sh get clients/\$CLIENT_UUID/protocol-mappers/models -r pulse 2>/dev/null | grep -B2 'realm-roles-mapper' | grep id | tr -d ' \"id:,')

  if [ -n \"\$MAPPER_ID\" ]; then
    /opt/keycloak/bin/kcadm.sh delete clients/\$CLIENT_UUID/protocol-mappers/models/\$MAPPER_ID -r pulse
    echo 'Ancien mapper supprimé'
  fi

  /opt/keycloak/bin/kcadm.sh create clients/\$CLIENT_UUID/protocol-mappers/models -r pulse \
    -s name=realm-roles-mapper \
    -s protocol=openid-connect \
    -s protocolMapper=oidc-usermodel-realm-role-mapper \
    -s consentRequired=false \
    -s 'config={\"claim.name\":\"roles\",\"multivalued\":\"true\",\"access.token.claim\":\"true\",\"id.token.claim\":\"true\",\"userinfo.token.claim\":\"true\"}'

  echo '✅ Mapper créé'
"
```


### Étape 7 — Relancer le container

```
docker stop wazuh-dashboard && docker rm wazuh-dashboard
docker compose up -d wazuh-dashboard
sleep 40
```


### Étape 8 — Accéder à l'application

Ouvre **https://ai.pulse.local** dans ton navigateur et connecte-toi avec un des comptes ci-dessous.
---

## Configuration

### Fichier `.env`

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `LLM_API_KEY` | Clé API OpenRouter ou Ollama | **Oui** |
| `DOCUMENTS_ENCRYPTION_KEY` | Clé hex 32 chars pour le chiffrement | **Oui** |
| `LLM_PROVIDER` | `openrouter` ou `ollama` | Non (défaut: openrouter) |
| `LLM_MODEL` | Modèle LLM à utiliser | Non |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL admin | Non |
| `KEYCLOAK_ADMIN_PASSWORD` | Mot de passe admin Keycloak | Non |
| `WAZUH_INDEXER_PASSWORD` | Mot de passe admin Wazuh | Non |
| `REDIS_PASSWORD` | Mot de passe Redis | Non |
| `MINIO_ROOT_PASSWORD` | Mot de passe MinIO | Non |

### Générer les valeurs manquantes

```bash
# Clé de chiffrement documents
openssl rand -hex 32

# Vérifier les variables non renseignées
grep "REMPLACER" .env
```

---

## Comptes de test

Ces comptes sont créés automatiquement lors de l'import du realm Keycloak.

> **Note** : Keycloak peut demander de changer le mot de passe au premier login — c'est normal, choisis un nouveau mot de passe.

| Utilisateur | Rôle | Accès |
|-------------|------|-------|
| `admin.technique` | Admin | Tout + Console admin + Wazuh |
| `karim.tazi` | RH | Dashboard RH, imports, employés, documents |
| `fatima.alaoui` | Manager | Dashboard manager, équipe, entretiens |
| `sara.bennani` | Direction | Dashboard direction, simulations, rapports |
| `youssef.benali` | Collaborateur | Mon espace, congés, formations, documents perso |

Les mots de passe sont définis dans `keycloak/exports/pulse-realm.json`.

---

## URLs des services

Tous les services sont accessibles après `./setup.sh` depuis **ta machine** (pas seulement dans la VM).

| Service | URL | Identifiants |
|---------|-----|--------------|
| Application principale | https://ai.pulse.local | Comptes Keycloak |
| Keycloak (SSO) | https://auth.pulse.local | `admin` / `KEYCLOAK_ADMIN_PASSWORD` du .env |
| Grafana (Monitoring) | https://grafana.pulse.local | `admin` / mot de passe dans .env |
| Prometheus (Métriques) | https://prometheus.pulse.local | — |
| Wazuh (SIEM) | https://wazuh.pulse.local | Compte avec rôle `admin` |
| Traefik (Dashboard) | https://traefik.pulse.local | `admin` / `admin` |

---

## Structure du projet

```
pulserh/
├── setup.sh                          # Script d'installation principal
├── docker-compose.yml                # Orchestration de tous les services
├── .env.example                      # Template des variables d'environnement
├── INSTALL.md                        # Guide d'installation résumé
│
├── pulseAIFront/                     # Frontend React
│   ├── src/
│   │   ├── pages/
│   │   │   ├── collaborateur/        # Vues collaborateur
│   │   │   ├── manager/              # Vues manager
│   │   │   ├── rh/                   # Vues RH
│   │   │   ├── direction/            # Vues direction
│   │   │   └── admin/                # Console admin
│   │   └── config/
│   │       ├── keycloak.js           # Configuration SSO
│   │       └── roles.js              # Définition des rôles
│   └── Dockerfile                    # Build multi-stage node → nginx
│
├── pulseAIBackend/                   # Backend FastAPI
│   ├── app/
│   │   ├── main.py                   # Point d'entrée
│   │   ├── routers/                  # Routes API (employees, leaves, docs, chat...)
│   │   ├── services/
│   │   │   ├── rag_service.py        # Service RAG (Qdrant + LLM)
│   │   │   ├── llm_client.py         # Client LLM (OpenRouter/Ollama)
│   │   │   └── ai_tools.py           # Outils IA
│   │   └── models/                   # Modèles SQLAlchemy
│   └── alembic/                      # Migrations base de données
│
├── keycloak/
│   ├── exports/
│   │   └── pulse-realm.json          # Realm complet avec users et clients
│   └── init-realm.sh                 # Script d'import du realm
│
├── traefik/
│   ├── traefik.yml                   # Config Traefik principale
│   ├── dynamic/
│   │   ├── routes.yml                # Routes vers les services
│   │   ├── middlewares.yml           # Middlewares (rate-limit, headers)
│   │   └── tls.yml                   # Config TLS
│   └── certs/                        # Certificats générés par setup.sh
│       ├── pulse.crt                 # ← À installer dans le navigateur
│       └── pulse.key
│
├── wazuh/
│   ├── config/
│   │   ├── wazuh-indexer.yml         # Config OpenSearch
│   │   ├── wazuh-dashboard.yml       # Config Kibana/Dashboard
│   │   ├── opensearch-security-config.yml  # Auth OpenID + rôles
│   │   ├── roles_mapping.yml         # Mapping rôles Keycloak → OpenSearch
│   │   └── internal_users.yml        # Utilisateurs internes Wazuh
│   ├── rules/
│   │   └── pulse_rules.xml           # Règles de détection personnalisées
│   └── certs/                        # Certificats Wazuh générés par setup.sh
│
├── postgres/
│   └── init.sh                       # Crée les 3 bases de données au démarrage
│
├── redis/
│   └── redis.conf                    # Config Redis avec auth
│
├── prometheus/
│   └── prometheus.yml                # Config scraping métriques
│
└── grafana/
    └── grafana.ini                   # Config Grafana + SSO Keycloak
```

---

## Fonctionnalités par rôle

### 👤 Collaborateur (`youssef.benali`)
- Mon tableau de bord personnel
- Gestion de mes congés (demande, solde, historique)
- Mes formations et compétences
- Mes documents RH (fiches de paie, attestations)
- Assistant IA pour questions RH personnelles
- Mon profil et préférences

### 👥 Manager (`fatima.alaoui`)
- Tableau de bord équipe
- Validation des congés de l'équipe
- Entretiens annuels et suivi performance
- Onboarding des nouveaux collaborateurs
- Prédictions de performance et insights IA
- Rapports d'équipe

### 🗂️ RH (`karim.tazi`)
- Gestion complète des employés
- Import de données (CSV, Excel)
- Génération de documents (contrats, attestations)
- Gestion des formations organisationnelles
- Analyse des talents et compétences
- Assistant IA pour analyse de CVs

### 📊 Direction (`sara.bennani`)
- Dashboard exécutif
- Simulations et scénarios RH
- Rapports stratégiques
- Prédictions de turnover
- Insights organisationnels globaux

### 🔧 Admin (`admin.technique`)
- Console d'administration complète
- Monitoring (Grafana, Prometheus)
- SIEM Wazuh (alertes de sécurité)
- Gestion des utilisateurs Keycloak
- Journaux d'audit

---

## Commandes utiles

### Vérifier l'état des services

```bash
docker compose ps
```

### Voir les logs d'un service

```bash
docker logs pulse_backend -f
docker logs pulse_keycloak -f
docker logs wazuh-dashboard -f
docker logs wazuh-indexer -f
```

### Relancer un service spécifique

```bash
docker compose restart backend
docker compose restart wazuh-dashboard
```

### Migrations manuelles

```bash
docker exec pulse_backend python -m alembic upgrade head
```

### Réinitialiser complètement (⚠️ efface toutes les données)

```bash
docker compose down -v
./setup.sh
```

### Réinitialiser uniquement Wazuh (garde les données app)

```bash
docker compose down wazuh-indexer wazuh-manager wazuh-dashboard
docker volume rm pulse-rh_wazuh_indexer_data
docker compose up -d
# Attendre 2 min puis :
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
```

### Tester depuis une VM (machine vierge)

```bash
# Installer Multipass
sudo snap install multipass       # Linux
brew install multipass             # macOS

# Créer une VM vierge
multipass launch --name pulse-test --cpus 4 --memory 8G --disk 40G
multipass shell pulse-test

# Dans la VM :
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu && newgrp docker
sudo apt install -y openssl git
git clone https://github.com/LostWin/pulserh.git
cd pulserh && git checkout dev
./setup.sh
```

---

## Dépannage

### Le setup s'arrête en demandant de remplir `.env`

Normal au premier lancement. Ouvre `.env`, renseigne `LLM_API_KEY` et `DOCUMENTS_ENCRYPTION_KEY`, puis relance `./setup.sh`.

### Keycloak ne démarre pas

```bash
docker logs pulse_keycloak 2>&1 | tail -20
```

Cause fréquente : mot de passe PostgreSQL invalide dans `.env`. Vérifier `KEYCLOAK_DB_PASSWORD`.

### `Invalid parameter: redirect_uri` sur ai.pulse.local

Le client `pulse-web` n'a pas la bonne redirect URI. Corriger manuellement :

```bash
docker exec -it pulse_keycloak /bin/bash -c "
  /opt/keycloak/bin/kcadm.sh config credentials \
    --server http://localhost:8080 --realm master \
    --client admin-cli \
    --user \$KEYCLOAK_ADMIN --password \$KEYCLOAK_ADMIN_PASSWORD
  CLIENT_ID=\$(/opt/keycloak/bin/kcadm.sh get clients -r pulse \
    --fields id,clientId | grep -B1 'pulse-web' | grep id | tr -d ' \"id:,')
  /opt/keycloak/bin/kcadm.sh update clients/\$CLIENT_ID -r pulse \
    -s 'redirectUris=[\"https://ai.pulse.local/*\",\"http://localhost:5173/*\"]' \
    -s 'webOrigins=[\"https://ai.pulse.local\",\"http://localhost:5173\"]'
"
```

### Bad Gateway sur wazuh.pulse.local

```bash
docker logs wazuh-dashboard 2>&1 | tail -10
```

Si le dashboard ne démarre pas, attendre 60s et réessayer. Si l'erreur persiste :

```bash
docker compose restart wazuh-dashboard
```

### 401 Unauthorized sur wazuh.pulse.local après connexion

R�initialiser la config de sécurité OpenSearch :

```bash
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
```

### Firefox bloque les requêtes API (CORS / certificat)

Les requêtes JavaScript vers `https://api.pulse.local` nécessitent que le certificat CA soit installé dans Firefox (pas seulement accepté via le bouton "Accepter le risque"). Voir [Installer le certificat TLS](#installer-le-certificat-tls).

### Les certificats sont générés mais demandent une passphrase

Utiliser `./setup.sh` — il génère les certificats via un fichier script sans jamais demander de passphrase. Ne pas copier-coller les commandes openssl directement dans le terminal.

### `/etc/hosts` n'a pas été modifié (permission denied)

```bash
echo "127.0.0.1 ai.pulse.local api.pulse.local auth.pulse.local wazuh.pulse.local grafana.pulse.local prometheus.pulse.local traefik.pulse.local" | sudo tee -a /etc/hosts
```

---

## Architecture technique détaillée

### Stack technologique

| Couche | Technologie | Version |
|--------|-------------|---------|
| Frontend | React + Vite + Tailwind | Node 20 |
| Backend | FastAPI + SQLAlchemy + Alembic | Python 3.11 |
| Base de données | PostgreSQL | 16 |
| Cache | Redis | 7 |
| Vector DB | Qdrant | latest |
| Object Storage | MinIO | latest |
| SSO | Keycloak | 25.0 |
| Reverse Proxy | Traefik | v3.1 |
| Monitoring | Prometheus + Grafana | v2.53 / 11.1 |
| SIEM | Wazuh (Indexer + Manager + Dashboard) | 4.8.0 |
| LLM | OpenRouter (Mistral, Claude, GPT) ou Ollama | — |

### Flux d'authentification

```
Utilisateur → https://ai.pulse.local
     │
     ▼
Traefik (TLS termination)
     │
     ▼
Frontend React
     │ Redirect login
     ▼
Keycloak (https://auth.pulse.local)
     │ Token JWT (PKCE)
     ▼
Frontend → API calls avec Bearer token
     │
     ▼
Backend FastAPI (validation JWT via JWKS)
     │
     ▼
PostgreSQL / Redis / Qdrant / MinIO
```

### Rôles et permissions

| Rôle Keycloak | Backend permissions | Wazuh |
|---------------|---------------------|-------|
| `admin` | Tout | Accès complet (`all_access`) |
| `hr` | CRUD employés, imports, docs | Lecture |
| `manager` | Équipe, entretiens, onboarding | Lecture |
| `director` | Rapports, simulations | Lecture |
| `collaborator` | Données personnelles uniquement | — |

### Certificats TLS

Le setup génère une **CA auto-signée** (`wazuh/certs/root-ca.pem`) qui signe tous les certificats internes Wazuh, et un certificat Traefik séparé (`traefik/certs/pulse.crt`) pour le HTTPS public.

Les certificats sont valables **10 ans** et ne nécessitent pas de renouvellement en développement/test.

---

## Licence

Projet interne Ynov Campus Maroc — Y-Days 2026.
