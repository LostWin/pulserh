# PulseRH — Guide d'installation rapide

## Prérequis

| Outil | Version min | Installation |
|-------|-------------|--------------|
| Docker | 24+ | https://docs.docker.com/get-docker/ |
| Docker Compose | v2 | Inclus dans Docker Desktop |
| openssl | n'importe | `sudo apt install openssl` (Linux) |

> **RAM recommandée** : 8 Go minimum (Wazuh seul consomme 2-3 Go)

---

## Installation en 3 commandes

```bash
# 1. Cloner
git clone https://github.com/LostWin/pulserh.git
cd pulserh
git checkout dev

# 2. Configurer (copie le .env et génère les certs automatiquement)
./setup.sh
# → Si c'est la première fois, il va créer un .env depuis .env.example
# → Édite .env et mets ta clé LLM_API_KEY, puis relance

# 3. Relancer (si première fois, après avoir rempli .env)
./setup.sh
```

---

## Ce que fait setup.sh automatiquement

1. Vérifie les prérequis (docker, openssl)
2. Crée le `.env` depuis `.env.example` si absent
3. **Génère les certificats TLS** (`traefik/certs/` et `wazuh/certs/`)
4. Ajoute les domaines `.pulse.local` dans `/etc/hosts`
5. Démarre tous les services avec `docker compose up -d --build`
6. Attend que Keycloak soit healthy (jusqu'à 5 min)
7. Lance les migrations Alembic
8. Configure Wazuh

---

## Installer le certificat dans le navigateur

Pour que HTTPS fonctionne sans avertissement :

- **Chrome/Edge/Firefox (Linux)** : Importer `traefik/certs/pulse.crt` dans Paramètres → Confidentialité → Certificats → Autorités
- **Windows** : Double-clic sur `traefik/certs/pulse.crt` → Installer → Autorités de certification racines de confiance
- **macOS** : Double-clic → Trousseau → Toujours faire confiance

---

## Comptes de test

| Utilisateur | Mot de passe | Rôle |
|-------------|-------------|------|
| admin.technique | PulseRH@2026! | Admin |
| karim.tazi | PulseRH@2026! | RH |
| fatima.alaoui | PulseRH@2026! | Manager |
| sara.bennani | PulseRH@2026! | Direction |
| youssef.benali | PulseRH@2026! | Collaborateur |

> Les mots de passe sont définis dans `keycloak/exports/pulse-realm.json`.
> Keycloak demandera un changement au premier login (comportement normal).

---

## Commandes utiles

```bash
# Voir les logs d'un service
docker logs pulse_backend -f
docker logs pulse_keycloak -f

# Relancer uniquement le backend
docker compose restart backend

# Réinitialiser complètement (SUPPRIME les données)
docker compose down -v
./setup.sh

# Vérifier l'état des services
docker compose ps

# Migrations manuelles
docker exec pulse_backend python -m alembic upgrade head
```

---

## Architecture des services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | https://ai.pulse.local | Application React |
| Backend | https://api.pulse.local | FastAPI |
| Keycloak | https://auth.pulse.local | SSO / IAM |
| Grafana | https://grafana.pulse.local | Monitoring |
| Prometheus | https://prometheus.pulse.local | Métriques |
| Wazuh | https://wazuh.pulse.local | SIEM sécurité |
| Traefik | https://traefik.pulse.local | Reverse proxy (admin/admin) |

