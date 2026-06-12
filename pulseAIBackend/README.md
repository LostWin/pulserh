#  Pulse AI Backend

> **Backend intelligent pour la gestion des ressources humaines augmentée par l'IA.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

---

## Table des matières

- [Aperçu](#-aperçu)
- [Architecture](#-architecture)
- [Stack Technique](#-stack-technique)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Démarrage](#-démarrage)
- [API Endpoints](#-api-endpoints)
- [Sécurité](#-sécurité)
- [Infrastructure Docker](#-infrastructure-docker)
- [Structure du Projet](#-structure-du-projet)
- [Contribuer](#-contribuer)

---

##  Aperçu

**Pulse AI** est une plateforme RH de nouvelle génération qui combine l'intelligence artificielle et l'automatisation pour transformer la gestion des ressources humaines. Le backend fournit une API REST complète couvrant :

-  **Assistant conversationnel IA** — Chat RAG (Retrieval-Augmented Generation) pour répondre aux questions RH
-  **Prédictions ML** — Analyse du risque de départ, prévision du turnover
-  **Génération de documents** — Création automatique de contrats, attestations, fiches de paie
-  **Workflows agentiques** — Orchestration automatisée de l'onboarding/offboarding
-  **Alertes proactives** — Détection et notification des situations RH critiques
-  **Dashboard analytique** — KPIs consolidés pour la direction

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Traefik    │────▶│  FastAPI API  │
│  (React/Vue) │     │  (Reverse    │     │  (Uvicorn)   │
└─────────────┘     │   Proxy)     │     └──────┬───────┘
                    └──────────────┘            │
                                               ▼
                    ┌──────────────────────────────────────┐
                    │           Services Layer              │
                    ├──────────┬──────────┬────────────────┤
                    │ LLM      │ RAG      │ Embedding      │
                    │ Client   │ Service  │ Service        │
                    ├──────────┼──────────┼────────────────┤
                    │ Workflow │ Alerting │ Document       │
                    │ Engine   │ Service  │ Generator      │
                    └──────┬───┴────┬─────┴───────┬────────┘
                           │        │             │
                    ┌──────▼──┐ ┌───▼────┐ ┌──────▼──┐
                    │PostgreSQL│ │ Redis  │ │ Qdrant  │
                    │ (Data)   │ │(Cache) │ │(Vectors)│
                    └─────────┘ └────────┘ └─────────┘
                                    ┌─────────┐ ┌──────────┐
                                    │  MinIO   │ │ Keycloak │
                                    │(Storage) │ │  (IAM)   │
                                    └─────────┘ └──────────┘
```

---

##  Stack Technique

| Composant | Technologie | Description |
|-----------|-------------|-------------|
| **Framework** | FastAPI | API REST asynchrone haute performance |
| **Runtime** | Python 3.11+ | Langage principal |
| **Auth / IAM** | Keycloak + JWT | Authentification SSO, RBAC |
| **Base de données** | PostgreSQL 16 | Stockage relationnel |
| **Cache** | Redis 7 | Cache, rate limiting, sessions |
| **Vector DB** | Qdrant | Stockage et recherche d'embeddings |
| **Object Storage** | MinIO | Stockage de fichiers S3-compatible |
| **Reverse Proxy** | Traefik v3 | Routage, TLS, rate limiting |
| **Monitoring** | Prometheus | Métriques applicatives |
| **Containerisation** | Docker Compose | Orchestration des services |

---

##  Installation

### Prérequis

- **Python** 3.11 ou supérieur
- **Docker** et **Docker Compose** (pour l'infrastructure complète)
- **Git**

### Installation locale (développement)

```bash
# 1. Cloner le dépôt
git clone https://gitlab.com/pulse-rh/pulse-rh.git
cd pulse-rh

# 2. Basculer sur la branche du backend
git checkout pulse-ai-backend

# 3. Créer un environnement virtuel
python -m venv venv

# 4. Activer l'environnement virtuel
# Windows
.\venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 5. Installer les dépendances
pip install -r requirements.txt

# 6. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs
```

---

##  Configuration

Toute la configuration est centralisée via des **variables d'environnement** (fichier `.env`).

| Variable | Description | Défaut |
|----------|-------------|--------|
| `PROJECT_NAME` | Nom du projet | `Pulse AI Backend` |
| `VERSION` | Version de l'API | `1.0.0` |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql+asyncpg://...` |
| `REDIS_URL` | URL de connexion Redis | `redis://localhost:6379/0` |
| `MINIO_ENDPOINT` | Endpoint MinIO | `localhost:9000` |
| `QDRANT_HOST` | Host Qdrant | `localhost:6333` |
| `KEYCLOAK_PUBLIC_KEY` | Clé publique Keycloak (JWT) | — |
| `KEYCLOAK_ISSUER` | URL de l'issuer Keycloak | `http://localhost:8080/realms/pulse-ai` |
| `CORS_ORIGINS` | Origines CORS autorisées | `http://localhost:3000,...` |
| `LLM_API_URL` | URL du serveur LLM (vLLM/OpenAI) | `http://localhost:8000/v1` |
| `LOG_LEVEL` | Niveau de log | `INFO` |
| `RATE_LIMIT_GLOBAL` | Limite globale (req/fenêtre) | `100` |
| `RATE_LIMIT_CHAT` | Limite pour /chat (req/fenêtre) | `30` |
| `RATE_LIMIT_WINDOW` | Fenêtre de rate limiting (sec) | `60` |

Consultez le fichier [`.env.example`](.env.example) pour un template complet.

---

##  Démarrage

### Mode développement (local)

```bash
# Activer le venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Lancer le serveur avec hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est accessible sur : **http://localhost:8000**
Documentation Swagger : **http://localhost:8000/docs**
Documentation ReDoc : **http://localhost:8000/redoc**

### Mode Docker (infrastructure complète)

```bash
# Copier la configuration
cp .env.example .env

# Démarrer tous les services
docker compose up -d

# Vérifier les logs
docker compose logs -f api

# Arrêter les services
docker compose down
```

Services déployés :

| Service | Port | URL |
|---------|------|-----|
| **API Backend** | 8000 | Via Traefik : `https://api.pulse.local` |
| **PostgreSQL** | 5432 | `localhost:5432` |
| **Redis** | 6379 | `localhost:6379` |
| **Keycloak** | 8080 | `http://localhost:8080` |
| **MinIO** | 9000/9001 | API: `9000`, Console: `9001` |
| **Qdrant** | 6333/6334 | HTTP: `6333`, gRPC: `6334` |
| **Traefik Dashboard** | 8082 | `http://localhost:8082` |
| **Prometheus Metrics** | — | `https://api.pulse.local/metrics` |

---

##  API Endpoints

### Authentification (`/auth`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/auth/login` | Connexion utilisateur |
| `POST` | `/auth/register` | Inscription |
| `GET` | `/auth/me` | Profil de l'utilisateur connecté |

### Employés (`/employees`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/employees` | Liste des employés (paginée) |
| `POST` | `/employees` | Créer un employé |
| `GET` | `/employees/{id}` | Détails d'un employé |
| `PUT` | `/employees/{id}` | Modifier un employé |
| `DELETE` | `/employees/{id}` | Supprimer un employé |
| `POST` | `/employees/import` | Import en masse (CSV) |
| `GET` | `/employees/export` | Export en masse |

### Départements (`/departments`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/departments` | Liste des départements |
| `POST` | `/departments` | Créer un département |

### Chat IA (`/chat`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/chat` | Envoyer un message au chatbot RAG |
| `GET` | `/chat/history` | Historique des conversations |

### Documents (`/documents`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/documents/generate` | Générer un document RH |
| `GET` | `/documents` | Liste des documents |
| `GET` | `/documents/{id}/download` | Télécharger un document |

### Workflows (`/workflows`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/workflows` | Lancer un workflow |
| `GET` | `/workflows` | Liste des workflows |
| `GET` | `/workflows/{id}` | Statut d'un workflow |

### Prédictions (`/predictions`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/predictions/attrition` | Prédiction du risque de départ |
| `GET` | `/predictions/turnover` | Prévision du turnover |

### Alertes (`/alerts`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/alerts` | Liste des alertes actives |
| `PUT` | `/alerts/{id}/acknowledge` | Acquitter une alerte |

### Dashboard (`/dashboard`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/dashboard/metrics` | KPIs globaux |
| `GET` | `/dashboard/trends` | Tendances temporelles |

### Administration (`/admin`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/admin/logs` | Logs système |
| `GET` | `/admin/config` | Configuration IA |
| `PUT` | `/admin/guardrails` | Configurer les guardrails IA |

### Santé (`/health`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | État du système |
| `GET` | `/health/detailed` | État détaillé de chaque dépendance |

---

##  Sécurité

### Authentification JWT (Keycloak)

L'API utilise des tokens **JWT signés par Keycloak** pour l'authentification. Chaque requête protégée doit inclure un header :

```
Authorization: Bearer <token>
```

### RBAC (Role-Based Access Control)

Les rôles sont définis dans Keycloak et vérifiés par le middleware RBAC :

| Rôle | Accès |
|------|-------|
| `employee` | Lecture de son profil, chat IA |
| `manager` | Gestion de son équipe, dashboard |
| `hr_admin` | Gestion complète des employés, documents |
| `admin` | Accès total, administration système |

### Middleware de sécurité

- **Rate Limiting** — Protection contre les abus (configurable par endpoint)
- **CORS** — Origines autorisées définies dans `.env`
- **Logging structuré** — Traçabilité complète de chaque requête
- **Gestion d'erreurs uniforme** — Aucune fuite d'information interne

---

##  Infrastructure Docker

### Build de l'image

```bash
docker build -t pulse-ai-backend .
```

L'image utilise un **multi-stage build** pour minimiser la taille :
1. **Stage 1** (`dependencies`) — Compilation des dépendances Python
2. **Stage 2** (`runtime`) — Image finale avec utilisateur non-root

### Sécurité Docker

- Utilisateur non-root (`appuser`)
- Health check intégré (`/health`)
- 4 workers Uvicorn en production
- Aucun outil de compilation dans l'image finale

---

##  Structure du Projet
```
pulse-ai-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI (CORS, middlewares, routeurs)
│   ├── config.py               # Configuration centralisée (pydantic-settings)
│   ├── dependencies.py         # Injection de dépendances
│   ├── core/
│   │   ├── security.py         # Vérification JWT (Keycloak)
│   │   └── rbac.py             # Contrôle d'accès basé sur les rôles
│   ├── middleware/
│   │   ├── logging.py          # Logging structuré de chaque requête
│   │   └── rate_limit.py       # Rate limiting par IP / endpoint
│   ├── routers/
│   │   ├── auth.py             # Authentification & profil
│   │   ├── employees.py        # CRUD Employés
│   │   ├── departments.py      # Gestion organisationnelle
│   │   ├── chat.py             # Assistant IA (RAG)
│   │   ├── documents.py        # Génération de documents
│   │   ├── workflows.py        # Orchestration agentique
│   │   ├── predictions.py      # Modèles prédictifs
│   │   ├── alerts.py           # Alertes RH
│   │   ├── dashboard.py        # KPIs & métriques
│   │   ├── admin.py            # Console d'administration
│   │   └── health.py           # Surveillance système
│   ├── schemas/
│   │   ├── auth.py             # Schémas Pydantic — Auth
│   │   ├── employee.py         # Schémas Pydantic — Employés
│   │   ├── department.py       # Schémas Pydantic — Départements
│   │   ├── chat.py             # Schémas Pydantic — Chat
│   │   ├── document.py         # Schémas Pydantic — Documents
│   │   ├── workflow.py         # Schémas Pydantic — Workflows
│   │   ├── prediction.py       # Schémas Pydantic — Prédictions
│   │   ├── alert.py            # Schémas Pydantic — Alertes
│   │   ├── dashboard.py        # Schémas Pydantic — Dashboard
│   │   ├── admin.py            # Schémas Pydantic — Admin
│   │   └── health.py           # Schémas Pydantic — Health
│   └── services/
│       ├── llm_client.py       # Client LLM (vLLM / OpenAI)
│       ├── rag_service.py      # Pipeline RAG complet
│       ├── embedding_service.py # Service d'embeddings
│       ├── workflow_engine.py  # Moteur de workflows agentiques
│       ├── alerting_service.py # Service d'alertes proactives
│       └── document_generator.py # Générateur de documents
├── .env.example                # Template des variables d'environnement
├── .gitignore                  # Fichiers exclus de Git
├── .dockerignore               # Fichiers exclus du build Docker
├── Dockerfile                  # Image Docker multi-stage
├── docker-compose.yml          # Stack complète (7 services)
└── requirements.txt            # Dépendances Python
```

---

##  Contribuer

### Branches

| Branche | Description |
|---------|-------------|
| `main` | Branche principale stable |
| `pulse-ai-backend` | Backend Pulse AI |
| `develop` | Branche de développement |

### Workflow Git

```bash
# 1. Créer une branche feature
git checkout -b feature/ma-feature pulse-ai-backend

# 2. Committer vos changements
git add .
git commit -m "feat: description de la feature"

# 3. Pousser et créer une Merge Request
git push origin feature/ma-feature
```

### Conventions de commit

- `feat:` — Nouvelle fonctionnalité
- `fix:` — Correction de bug
- `docs:` — Documentation
- `refactor:` — Refactoring
- `test:` — Tests
- `chore:` — Maintenance

---

##  Licence

Projet propriétaire — © 2026 Pulse RH. Tous droits réservés.

---

<p align="center">
  Made with  by the <strong>Pulse AI Team</strong>
</p>
