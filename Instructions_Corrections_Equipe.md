# Instructions de correction — Version renforcée pour l'équipe

## 1. But de ce document

Ce document est un **template d'instructions renforcé** pour corriger les manquements identifiés lors de l'audit.

Il doit servir à l'équipe pour :

- corriger les écarts restants
- éviter de reproduire les mêmes erreurs
- livrer des lots réellement terminés
- améliorer la qualité d'exécution, pas seulement la vitesse

Ce document remplace toute consigne implicite par des consignes **explicites, vérifiables et non ambiguës**.

---

## 2. Constat d’audit à garder en tête

L’audit a montré que l’équipe a globalement bien respecté l’architecture, mais a commis plusieurs erreurs typiques :

### 2.1. Erreurs observées

- des écrans ont été enrichis visuellement sans que toutes les actions soient branchées
- certains lots ont été livrés comme “finis” alors qu’ils étaient en réalité “partiels”
- certaines couches backend ont été créées, mais sans niveau de finition suffisant
- l’import a utilisé un contournement dangereux en supprimant des clés étrangères pour “faire passer” les données
- la couverture de tests est insuffisante
- certaines décisions de fallback n’ont pas été assez signalées comme temporaires

### 2.2. Conséquence

Pour la suite :

- plus aucune implémentation ne doit être livrée comme “terminée” si elle est seulement amorcée
- plus aucun contournement silencieux sur la donnée ne doit être introduit
- plus aucune action UI ne doit être laissée décorative sans être explicitement marquée comme telle

---

## 3. Règles impératives à respecter

Ces règles sont **obligatoires**.

## 3.1. Interdiction de corriger un problème métier par dégradation silencieuse de la donnée

### Interdiction absolue

Il est interdit de :

- supprimer des relations pour faire passer un import
- nullifier automatiquement des `_id` sensibles en cas de problème de FK
- “désamorcer” une cohérence métier juste pour éviter une erreur

### Si une donnée parente manque

Il faut :

1. échouer proprement
2. enregistrer l’erreur de façon lisible
3. dire quelle dépendance est manquante
4. proposer l’ordre d’import attendu

### Exemple

Si une `mobility_request` pointe vers un `department_id` absent :

- ne pas remplacer `department_id` par `null`
- retourner une erreur d’import claire
- indiquer que `departments` doit être importé avant

### Règle d’or

> Si la donnée est incohérente, on le **signale**. On ne la “répare” pas silencieusement.

---

## 3.2. Interdiction de livrer un bouton décoratif comme une fonctionnalité terminée

Si un bouton, une action, un lien ou un CTA est affiché :

- il doit être réellement branché
- ou être explicitement désactivé
- ou être explicitement marqué “bientôt disponible”

### Interdit

- bouton cliquable sans action
- bouton visuellement actif mais non connecté
- bouton purement décoratif présenté comme fini

### Obligation

Pour chaque CTA :

- préciser sa destination
- préciser l’endpoint ou la navigation associée
- vérifier son comportement

---

## 3.3. Ne jamais déclarer un lot “fini” s’il est seulement partiel

Chaque livraison doit être classée dans l’une de ces 3 catégories :

- `complet`
- `partiel`
- `amorcé`

### Définitions

#### Complet

- backend fait
- front fait
- actions branchées
- états loading/error/empty gérés
- validation faite
- aucun workaround caché

#### Partiel

- structure principale faite
- mais il reste au moins un manque fonctionnel visible ou critique

#### Amorcé

- fondation posée
- mais pas encore exploitable comme fonctionnalité métier finalisée

### Interdiction

Il est interdit d’écrire “terminé”, “fait”, “livré” si le lot est seulement `partiel` ou `amorcé`.

---

## 3.4. Toujours préciser si un fallback est temporaire

Tout fallback doit être :

- visible dans le code
- documenté
- justifié
- identifiable comme temporaire ou structurel

### Il faut indiquer

- pourquoi le fallback existe
- quel risque il couvre
- ce qu’il faudra faire pour le remplacer

### Exemple acceptable

- fallback LLM si pas de tool-calling
- fallback internal calendar si pas de provider externe

### Exemple non acceptable

- fallback qui supprime des relations de données
- fallback qui masque un bug de modèle

---

## 3.5. Pas de logique métier lourde dispersée dans les routeurs

Le routeur doit :

- valider la requête
- appeler un service
- retourner la réponse

Il ne doit pas porter durablement :

- un gros calcul métier inline
- des règles complexes recopiées
- des heuristiques répétées sur plusieurs endpoints

### Règle

Si la logique est réutilisable ou métier :

- créer ou enrichir un service dédié

---

## 3.6. Toute donnée nouvelle doit suivre la logique import-first

Si vous ajoutez un nouveau domaine métier, vous devez vérifier s’il faut aussi :

- une migration
- un seed
- un endpoint d’import
- un sample CSV
- une doc d’ordre d’import

Si ce n’est pas fait, le lot n’est pas complet.

---

## 3.7. Toute donnée sensible doit être protégée au backend

### Interdit

- masquer uniquement côté front
- envoyer la vraie donnée au client puis la cacher en UI

### Obligatoire

- DAC appliqué côté backend
- `_field_visibility` cohérent
- preview admin DAC si nécessaire

---

## 4. Definition of Done obligatoire pour chaque ticket

Un ticket n’est considéré comme **terminé** que si tous les points ci-dessous sont validés.

## 4.1. Backend

- modèle/migration faits si nécessaire
- schémas API mis à jour
- service métier créé ou enrichi
- route branchée proprement
- pas de lazy-loading instable
- pas de contournement silencieux des données

## 4.2. Front

- écran branché au backend
- plus de mock front sur la fonctionnalité concernée
- états `loading`, `error`, `empty` gérés
- actions réellement connectées
- comportement cohérent avec DAC

## 4.3. Validation

- build front OK
- syntaxe backend OK
- smoke test fonctionnel fait
- Docker vérifié si le ticket touche un service exécuté

## 4.4. Documentation de fin de ticket

Le développeur doit fournir :

- statut : `complet`, `partiel` ou `amorcé`
- fichiers modifiés
- endpoints touchés
- validations exécutées
- limitations restantes
- risques connus

Sans ça, le ticket n’est pas recevable.

---

## 5. Format obligatoire de restitution par l’équipe

À la fin de chaque ticket, l’équipe doit fournir exactement cette structure :

## Ticket

- Nom du ticket
- Statut : `complet` / `partiel` / `amorcé`

## Backend

- Modèles touchés
- Services touchés
- Routeurs touchés
- Migrations ajoutées

## Front

- Pages touchées
- Composants touchés
- Actions branchées

## Validation

- Build front : `OK` / `KO`
- Py compile / tests backend : `OK` / `KO`
- Docker : `OK` / `KO`
- Smoke test : description courte

## Limites restantes

- ce qui n’est pas fini
- ce qui est fallback
- ce qui dépend d’une future étape

---

## 6. Ordre de correction recommandé des manquements actuels

L’équipe doit corriger dans cet ordre.

## 6.1. Priorité 1 — Corriger les écarts dangereux

### Ticket 1 — Import : supprimer le fallback qui nullifie les FK

Fichier concerné :

- `/Users/walidtraore/Documents/Ynov/Cours/Y-Days/Projets/PulseRH/pulseAIBackend/app/services/import_service.py`

### Objectif

Retirer la logique qui transforme silencieusement les `_id` en `null` en cas d’erreur d’intégrité.

### À faire

1. supprimer le fallback de suppression FK
2. conserver l’import échoué avec message clair
3. retourner la dépendance manquante si identifiable
4. documenter l’ordre d’import attendu

### Critère d’acceptation

Si une dépendance est absente :

- l’import échoue proprement
- la donnée n’est pas dégradée
- le message aide à corriger

---

## 6.2. Priorité 2 — Finaliser les actions RH visibles

### Ticket 2 — Brancher les CTA de la page RH Carrières

Fichier concerné :

- `/Users/walidtraore/Documents/Ynov/Cours/Y-Days/Projets/PulseRH/pulseAIFront/src/pages/rh/Carrieres.jsx`

### Objectif

Rendre les boutons :

- `Profil`
- `Carrière`
- `Revue`

réellement actionnables.

### À faire

1. `Profil` doit ouvrir la fiche collaborateur appropriée
2. `Carrière` doit ouvrir la vue carrière détaillée
3. `Revue` doit ouvrir la revue carrière ou la préparation d’entretien
4. si un écran n’existe pas encore, le bouton doit être :
   - désactivé
   - ou marqué explicitement “Bientôt disponible”

### Interdiction

Ne pas laisser un bouton actif sans action.

---

## 6.3. Priorité 3 — Clarifier ce qui est partiel

### Ticket 3 — Requalifier les lots réellement partiels

Objectif :

Repasser tous les lots récents et reclasser honnêtement :

- `complet`
- `partiel`
- `amorcé`

### À auditer

- RH Carrières
- Observabilité IA
- Prédictions V2
- Health/Redis
- Manager V2
- Reporting V2

### Livrable attendu

Un tableau markdown simple :

| Lot | Statut | Pourquoi | Prochaine étape |
|---|---|---|---|

---

## 6.4. Priorité 4 — Finir le lot RH pilotage

### Ticket 4 — Compléter la vue RH Carrières côté backend et front

À faire :

- filtres métiers plus riches
- tri robuste
- pagination si besoin
- manager / ancienneté / revue carrière
- actions branchées
- DAC complet sur les nouveaux champs

### Important

La page doit être considérée comme finie seulement si elle est **actionnable**, pas juste jolie.

---

## 6.5. Priorité 5 — Durcir la qualité des sprints avancés

### Ticket 5 — Prédictions V2 : passer de “service créé” à “lot vraiment stabilisé”

À faire :

- sortir les constantes magiques dans une config/service
- ne pas laisser `model_version="v2.0"` en dur si une stratégie de versionning est prévue
- documenter les heuristiques encore présentes
- vérifier la persistance des snapshots

### Ticket 6 — Observabilité IA : passer de journal d’events à pilotage

À faire :

- ajouter filtres période
- ajouter agrégats
- vérifier couverture réelle des usages IA
- expliciter les zones encore non instrumentées

### Ticket 7 — Redis / Health

À faire :

- qualifier l’état réel du rate limiting
- dire s’il est “résolu” ou seulement “dégradé mais toléré”
- enrichir les messages du health détaillé

---

## 7. Modèle de consigne à utiliser désormais pour chaque futur ticket

Copier-coller ce modèle pour chaque nouvelle demande à l’équipe.

---

# Ticket : [Nom du ticket]

## Objectif métier

Décrire en 3 à 5 lignes le but métier exact.

## Périmètre autorisé

- fichiers backend autorisés :
- fichiers front autorisés :
- migrations autorisées :
- seeds / imports concernés :

## Interdictions spécifiques

- ne pas introduire de mock front
- ne pas contourner une incohérence de données
- ne pas ajouter de CTA décoratif
- ne pas masquer une donnée sensible uniquement côté front

## Travail attendu — Backend

- modèles :
- services :
- routeurs :
- schémas :

## Travail attendu — Front

- pages :
- composants :
- comportements :

## Validation obligatoire

- `npm run build`
- `python3 -m py_compile ...`
- smoke test fonctionnel
- si Docker impacté : validation conteneur

## Definition of Done

Le ticket n’est accepté que si :

- backend branché
- front branché
- aucun bouton décoratif
- aucun fallback silencieux sur la donnée
- retour d’état clair : `complet`, `partiel` ou `amorcé`

## Format de restitution

- statut :
- fichiers :
- validations :
- limitations :
- prochaines étapes :

---

## 8. Précautions à garder pour les prochaines instructions

Pour les futures instructions données à l’équipe :

### Toujours préciser

- ce qui est interdit
- ce qui constitue un ticket terminé
- ce qui doit être testé
- ce qui doit être déclaré comme partiel

### Toujours demander

- un retour structuré
- une preuve de validation
- une liste des limites restantes

### Toujours éviter

- les consignes trop générales du style “finaliser”
- les formulations ambiguës comme “implémentez ça”
- les tickets trop larges sans sous-livrables

---

## 9. Message final à transmettre à l’équipe

Le problème principal de la précédente passe n’est pas un manque d’effort ni une mauvaise direction technique.

Le problème principal est :

- un niveau de finition inégal
- une qualification trop optimiste de certains lots
- et un ou deux contournements dangereux sur la donnée

L’objectif de cette nouvelle passe est donc simple :

> finir proprement, honnêtement, et sans compromis silencieux sur la cohérence métier.

