# YDAYS HR Platform

Plateforme RH augmentée par l'IA pour **anticiper le désengagement** et piloter les
ressources humaines. Prototype front-end React, avec 5 espaces métier (Collaborateur,
Manager, RH, Direction, Admin) et une authentification simulée par rôle.

## 🚀 Démarrage

```bash
npm install      # installer les dépendances
npm run dev      # serveur de développement (http://localhost:5173)
npm run build    # build de production
npm run preview  # prévisualiser le build
npm run lint     # vérifier le code
```

> **Connexion** : la page d'accueil propose un sélecteur de rôle (auth simulée).
> Choisissez un profil pour entrer dans l'espace correspondant. La session est
> conservée dans le `localStorage`.

## 🧱 Stack

- **React 19** + **React Router 7**
- **Vite** (build & HMR)
- **Tailwind CSS v4** (config CSS-first via `@import "tailwindcss"`)
- **Recharts** (graphiques) · **lucide-react** (icônes)
- `clsx` + `tailwind-merge` pour la composition de classes

## 📁 Structure

```
src/
├─ config/roles.js        # source unique des rôles, accueils & navigation
├─ contexts/AuthContext   # auth simulée (login/logout, persistance)
├─ data/mockData.js       # données de démo partagées par tous les écrans
├─ lib/utils.js           # cn() + helpers engagement/risque
├─ components/
│  ├─ ui/                 # design system : Card, StatCard, Badge, Avatar…
│  ├─ ProtectedRoute.jsx  # garde d'accès par rôle/section
│  ├─ PageHeader.jsx
│  └─ ComingSoon.jsx
├─ layouts/Layout.jsx     # sidebar + topbar + drawer mobile
└─ pages/
   ├─ Login.jsx · NotFound.jsx
   ├─ collaborateur/  (Dashboard, Assistant IA, Congés, Documents, Profil, Onboarding)
   ├─ manager/        (Dashboard, Mon Équipe, Prédictions)
   ├─ rh/             (Dashboard, Employés, Départements)
   ├─ direction/      (Dashboard, Simulations)
   └─ admin/          (Monitoring)
```

## ✅ Écrans construits

- **Collaborateur** *(espace complet)* — Dashboard personnel (engagement, humeur),
  **Assistant IA** (chat interactif simulé), **Congés** (demande + historique stateful),
  Documents, Profil et Onboarding.
- **Manager** — Dashboard équipe (watchlist IA), **Mon Équipe** (roster filtrable) et
  **Prédictions IA** (risque de départ + facteurs explicatifs).
- **RH** — Dashboard global, **table des employés** (recherche & filtres) et Départements.
- **Direction** — Dashboard stratégique et **Simulateur de scénarios** (leviers interactifs,
  projections d'engagement / turnover / ROI en temps réel).
- **Admin** — **Monitoring** système (services, trafic, journal d'audit).

Les modules restants affichent un écran « Bientôt disponible » et restent
entièrement navigables.

## 🗺️ Prochaines étapes

- Brancher une **authentification réelle** (Keycloak / OIDC) à la place de la simulation.
- Connecter un **backend / API** et remplacer `data/mockData.js`.
- Construire les modules restants (congés, prédictions détaillées, simulations, etc.).
- Migration progressive vers **TypeScript** et ajout de tests.
