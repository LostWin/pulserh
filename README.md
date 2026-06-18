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

## 🏗️ Architecture Globale (Pulse AI + Sécurité)

**Pulse AI** est une plateforme RH de nouvelle génération qui combine l'intelligence artificielle et l'automatisation pour transformer la gestion des ressources humaines, tout en garantissant un niveau de sécurité militaire grâce à Wazuh et Keycloak.

```text
Internet (HTTPS)
│
▼
┌────────────────────────────────────────────────────────┐
│                      Traefik v3.1                       │
│    Reverse proxy + TLS (Auto-routing via domaines)      │
│  (ai, api, auth, traefik, prometheus, grafana, wazuh)   │
└─┬─────────────────────┬───────────────────────┬────────┘
  │                     │                       │
  ▼                     ▼                       ▼
┌──────────────┐  ┌────────────────────┐  ┌────────────────────────┐
│  Frontend    │  │    Pulse AI API    │  │  Services Applicatifs  │
│ (React/Vite) │  │  (FastAPI / RAG)   │  │                        │
│ ai.pulse...  │  │   api.pulse...     │  │  - Grafana (port 3000) │
└──────┬───────┘  └────────┬───────────┘  │  - Wazuh Dash (5601)   │
       │                   │              │  - Prometheus (9090)   │
       │                   │              └────────────┬───────────┘
       │                   ▼                           │
       │          ┌───────────────────┐                │
       │          │ LLM, RAG, Workflows│                │
       │          │ Alerting, Docs     │                │
       │          └────┬──────┬───────┘                │
       ▼               ▼      ▼                        ▼
┌──────────────┐  ┌────────┐ ┌────────┐   ┌────────────────────────┐
│   Keycloak   │  │ Redis  │ │ Qdrant │   │  Wazuh Indexer /       │
│  (SSO / IAM) │  │(Cache) │ │(Vector)│   │  Wazuh Manager         │
│ auth.pulse...│  └────────┘ └────────┘   │  (Règles de sécurité)  │
└──────┬───────┘                          └────────────────────────┘
       │               ▲
       ▼               │
┌──────────────────────┴┐    ┌─────────┐
│      PostgreSQL       │    │  MinIO  │
│  (multi-DB : Keycloak,│    │(Storage)│
│   Backend AI)         │    └─────────┘
└───────────────────────┘
```

### 🧩 Composants Clés
- **Frontend (Pulse RH)** : Interface utilisateur (React/Vite)
- **Pulse AI Backend** : API REST asynchrone (FastAPI) pilotant le chatbot RH (RAG), les prédictions ML, et les workflows agentiques.
- **Keycloak** : Gestion des identités (IAM) et Single Sign-On (SSO).
- **PostgreSQL / Redis** : Stockage relationnel et cache distribué.
- **Qdrant / MinIO** : Base de données vectorielle (pour le RAG) et stockage de fichiers S3-compatible (documents RH).
- **Wazuh / Grafana** : SIEM pour la sécurité et monitoring système.

### 🛡️ Résilience et Rate Limiting (Fail-Open)
Pulse AI intègre un mécanisme de **Rate Limiting via Redis** (Token Bucket, 100 requêtes globales / minute, 30 requêtes sur /chat).
En cas de défaillance du cache Redis, la plateforme adopte un comportement **Fail-Open** (dégradé mais accepté) : le rate limiting est temporairement ignoré pour ne pas bloquer l'usage RH vital de l'entreprise. Cet état dégradé est visible en temps réel dans l'interface de supervision de l'administrateur technique.
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
127.0.0.1 ai.pulse.local
```

### 3. Fichier d'environnement (⚠️ Obligatoire)

Le conteneur de base de données PostgreSQL ne démarrera pas sans les mots de passe.

```bash
cp .env.example .env
# Éditer .env si nécessaire (mots de passe, etc.)
```

### 4. Générer les certificats de sécurité locaux

Puisque les certificats HTTPS sont ignorés par Git pour des raisons de sécurité, **vous devez les générer manuellement** avant de lancer Docker, sinon les dossiers seront créés vides et Wazuh plantera.

Exécutez cette commande à la racine du projet (fonctionne sous Mac/Linux) :

```bash
rm -rf wazuh/certs traefik/certs && mkdir -p wazuh/certs traefik/certs

# Certificats Wazuh
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout wazuh/certs/root-ca.key -out wazuh/certs/root-ca.pem -subj "/C=MA/ST=Casa/L=Casa/O=Pulse/CN=RootCA"
for i in indexer manager dashboard; do
  openssl req -new -nodes -newkey rsa:2048 -keyout wazuh/certs/$i.key -out wazuh/certs/$i.csr -subj "/C=MA/ST=Casa/L=Casa/O=Pulse/CN=$i"
  openssl x509 -req -in wazuh/certs/$i.csr -CA wazuh/certs/root-ca.pem -CAkey wazuh/certs/root-ca.key -CAcreateserial -out wazuh/certs/$i.pem -days 365
done
cp wazuh/certs/root-ca.pem wazuh/certs/indexer-trust.crt
cp wazuh/certs/root-ca.pem wazuh/certs/ca-bundle.crt

# Certificats Traefik (SSO & Frontend)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout traefik/certs/pulse.key -out traefik/certs/pulse.crt -subj "/C=MA/ST=Casa/L=Casa/O=Pulse/CN=*.pulse.local"

chmod -R 755 wazuh/certs traefik/certs
```

### 5. Faire confiance au certificat (Spécial macOS)

Sur macOS (Safari / Firefox), le système bloquera l'accès à `ai.pulse.local` en raison du protocole HSTS et du fait que le certificat est auto-signé.
Pour autoriser la navigation, ajoutez le certificat fraîchement créé au trousseau d'accès de votre Mac :

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain traefik/certs/pulse.crt
```
> **Attention :** Pensez à fermer complètement votre navigateur et à le relancer pour que cela prenne effet.

### 6. Lancer la stack

```bash
# Sur certaines installations Mac, il faut utiliser "docker-compose" avec un tiret
docker-compose up -d --build
```

> Attendre que tous les services soient **healthy** (vérifier avec `docker compose ps`).
> Le premier démarrage peut prendre quelques minutes (téléchargement des images, initialisation).

### 7. Accéder aux services

| Service             | URL                              | Identifiants / Authentification                        |
|---------------------|----------------------------------|--------------------------------------------------------|
| **Pulse RH (Frontend)** | **https://ai.pulse.local**     | SSO Keycloak (ex: `youssef.benali` / `Pulse@Collab26`) |
| Traefik Dashboard   | https://traefik.pulse.local      | Basic Auth (voir `.env`)                              |
| Keycloak Admin      | https://auth.pulse.local/admin   | `admin` / `PulseRH_AdminKC_2026Secure`                |
| Prometheus          | https://prometheus.pulse.local   | aucune                                                 |
| Grafana             | https://grafana.pulse.local      | SSO Keycloak (bouton "Log in with Keycloak")          |
| Wazuh Dashboard     | https://wazuh.pulse.local        | SSO Keycloak (redirection automatique)                |

> **Note :** Les certificats sont auto‑signés, votre navigateur affichera un avertissement. Acceptez‑le.
> **IMPORTANT (Firefox) :** Si vous obtenez une erreur du type `NetworkError when attempting to fetch resource`, c'est parce que Firefox bloque silencieusement les requêtes vers l'API et Keycloak en raison du certificat auto-signé. Pour résoudre cela, ouvrez les liens suivants dans un nouvel onglet et acceptez le risque pour chacun d'eux :
> - [https://api.pulse.local/health](https://api.pulse.local/health)
> - [https://auth.pulse.local](https://auth.pulse.local)

### 8. Générer et importer les données RH de démonstration

Le projet inclut un script Python qui génère des données RH réalistes (105 employés, 3-5 ans d'historique) dans 21 fichiers CSV. Ces données alimentent les dashboards, le chatbot IA et les modèles de Machine Learning.

#### 8.1 Générer les fichiers CSV

```bash
cd pulseAIBackend
python3 -m scripts.generate_csv
```

> Le script crée un dossier `data_imports/` contenant 21 fichiers CSV numérotés de `01_departments.csv` à `21_promotion_history.csv`.
> La génération prend quelques secondes (~59 000 lignes de présence, ~3 000 snapshots d'engagement, ~1 500 congés, etc.).

#### 8.2 Importer les données dans Pulse AI

Les fichiers doivent être importés **dans l'ordre numérique** pour respecter les dépendances entre entités (un employé doit exister avant ses congés, etc.).

1. Connectez-vous à **https://ai.pulse.local** avec un compte admin (ex: `admin.technique` / `Pulse@Admin2026`)
2. Allez dans le menu **Administration** → **Imports**
3. Importez les fichiers un par un dans l'ordre suivant :

| Ordre | Fichier | Contenu | Dépendances |
|-------|---------|---------|-------------|
| 1 | `01_departments.csv` | 6 départements | — |
| 2 | `02_jobs.csv` | 33 postes | — |
| 3 | `03_employees.csv` | 105 employés | Départements, Postes |
| 4 | `04_contracts.csv` | ~140 contrats | Employés |
| 5 | `05_leaves.csv` | ~1 500 congés | Employés |
| 6 | `06_projects.csv` | 25 projets | Employés (manager) |
| 7 | `07_tasks.csv` | ~420 tâches | Projets, Employés |
| 8 | `08_attendances.csv` | ~59 000 présences | Employés |
| 9 | `09_skills.csv` | 8 compétences | — |
| 10 | `10_employee_skills.csv` | ~315 compétences | Employés, Compétences |
| 11 | `11_training_courses.csv` | 6 formations | Compétences |
| 12 | `12_training_enrollments.csv` | ~170 inscriptions | Employés, Formations |
| 13 | `13_project_assignments.csv` | ~190 affectations | Projets, Employés |
| 14 | `14_engagement_snapshots.csv` | ~3 000 snapshots | Employés |
| 15 | `15_performance_reviews.csv` | ~530 revues | Employés |
| 16 | `16_performance_objectives.csv` | ~480 objectifs | Employés |
| 17 | `17_benefit_plans.csv` | 3 plans avantages | — |
| 18 | `18_employee_benefits.csv` | ~315 rattachements | Employés, Plans |
| 19 | `19_career_paths.csv` | 105 parcours | Employés, Postes |
| 20 | `20_mobility_requests.csv` | ~20 demandes | Employés, Départements |
| 21 | `21_promotion_history.csv` | ~16 promotions | Employés |

> **💡 Astuce :** Vous pouvez aussi télécharger le kit d'import complet (avec un README détaillé) directement depuis l'interface via le bouton **Télécharger les exemples** de la page d'import.

#### 8.3 Entraîner les modèles de Machine Learning

Une fois les données importées, lancez l'entraînement des modèles ML depuis l'interface :

1. Allez dans **Administration** → **Intelligence Artificielle** → onglet **Modèles ML**
2. Pour chaque module en mode ML (`CHURN_RISK`, `ABSENTEEISM`, `SECURITY_ANOMALY`), cliquez sur **Entraîner**
3. Le statut passe de "Non entraîné" à "En cours..." puis "Prêt" une fois l'entraînement terminé

> **⚠️ Important :** Le module `ABSENTEEISM` nécessite au minimum 30 jours de données de présence pour s'entraîner. Le script de génération en produit 3 ans, ce qui est largement suffisant.

---

## 🧪 Tester l'Intelligence Artificielle (Scénarios)

Le système intègre 5 modules d'intelligence artificielle. Voici comment les tester de manière optimale après avoir importé les données :

### 🤖 Modèles pré-entraînés (Fonctionnels instantanément)

Ces modules utilisent des algorithmes directs ou des modèles HuggingFace (téléchargés automatiquement) et **ne nécessitent pas d'entraînement manuel** de votre part.

#### 1. Analyse de Sentiment (Dashboard Manager / RH)
*Ce modèle détecte l'humeur des collaborateurs à partir de leurs feedbacks.*
- **Comment tester :** Connectez-vous avec plusieurs collaborateurs (ou modifiez des données en base) et laissez des feedbacks très marqués (ex: *"Je suis à bout, trop de surcharge de travail"*). 
- **Résultat :** Allez sur le dashboard Manager. Le modèle ML (DistilCamemBERT) catégorisera automatiquement ces phrases et, si le seuil d'alertes négatives est dépassé, affichera une alerte de "Risque d'engagement" pour le département.

#### 2. Recommandation de Formation (Espace Collaborateur)
*Ce module utilise l'analyse d'écarts (Gap Analysis / Cosinus Similarité) pour suggérer des formations.*
- **Comment tester :** Assurez-vous qu'un employé a une compétence faible (ex: *Management 1/5*) et qu'une formation cible cette compétence. Connectez-vous avec cet employé.
- **Résultat :** Dans la section formations, le moteur ML calculera l'écart et lui recommandera de lui-même la formation pertinente avec un score de pertinence élevé.

### 📈 Modèles sur-mesure (À entraîner)

Les modules suivants doivent analyser l'historique de **votre** base de données pour apprendre les comportements. Vous devez cliquer sur **"Entraîner"** dans l'onglet *Config IA*.

#### 3. Risque de départ (Churn Risk)
- **Comment tester :** Modifiez les données d'un employé pour simuler un mal-être (beaucoup d'absences, solde de congés négatif, revues de performances basses).
- **Résultat :** Après avoir cliqué sur "Entraîner" dans l'administration, le modèle XGBoost s'entraînera. Le dashboard RH remontera alors cet employé avec une alerte de "Risque de départ".

#### 4. Anomalies de Sécurité (Isolation Forest)
- **Comment tester :** Les collaborateurs effectuent des actions normales en journée. Injectez via la base (ou simulez des requêtes massives) un comportement anormal pour un utilisateur à 3h du matin (ex: téléchargement de dizaines de documents).
- **Résultat :** Une fois entraîné, le modèle détectera ce comportement comme étant "hors norme" et générera une alerte de sécurité.

> **🛡️ Note de robustesse (Fallback) :** Tous les systèmes disposent d'un Fallback Heuristique. Si le modèle ML n'est pas encore entraîné ou si un appel réseau échoue, le système bascule automatiquement sur des règles classiques pour que l'application ne plante jamais.

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

> ⚠️ **API Wazuh Manager** : l'API (port 55000) n'est pas configurée dans cette version.
> Les fonctionnalités nécessitant l'API (Ruleset Test, gestion des agents) ne sont donc pas disponibles.
> Le dashboard reste pleinement utilisable pour la consultation des alertes et des logs (via Discover, Dev Tools, Visualize).

---

## 📁 Structure du projet

```
pulse-rh-security/
├── docker-compose.yml           # Stack Docker Compose complète
├── .env.example                 # Modèle de variables d'environnement
├── setup-hosts.sh               # Ajoute les domaines locaux dans /etc/hosts
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

Le backend doit envoyer les événements de sécurité **directement dans l'indexer Wazuh (OpenSearch)**.

- **Endpoint** : `https://wazuh-indexer:9200/wazuh-alerts-YYYY.MM.DD/_doc`
- **Authentification** : `admin` / `PulseWazuh_Indexer2026!`
- **Format JSON** :

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "user_id": "uuid",
  "role": "collaborator",
  "action": "chat_request",
  "endpoint": "/chat",
  "status": "REFUSED",
  "reason": "prompt_injection_detected",
  "ip": "192.168.1.1"
}
```

**Implémentation Python (exemple) :**

```python
import requests
import datetime

log = {
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "user_id": "6d5cfe65-...",
    "role": "collaborator",
    "action": "chat_request",
    "status": "REFUSED",
    "reason": "prompt_injection_detected",
    "ip": "192.168.1.1",
}

requests.post(
    f"https://wazuh-indexer:9200/wazuh-alerts-{datetime.date.today().strftime('%Y.%m.%d')}/_doc",
    auth=("admin", "PulseWazuh_Indexer2026!"),
    json=log,
    verify=False,  # certificats auto-signés
)
```

> **Note :** Les logs sont indexés immédiatement et consultables via Dev Tools ou l'API. L'affichage dans Discover peut présenter un bug avec le champ `timestamp`, mais les données sont bien présentes.

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

- **Logs non visibles dans Discover** : si le message `Could not locate that index-pattern-field (id: timestamp)` apparaît, utilisez **Dev Tools** ou **Visualize** pour interroger les données. Les logs sont bien présents dans OpenSearch. Ce bug est lié à la création manuelle d'index.
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
