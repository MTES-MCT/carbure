# CarbuRe React frontend

## Commands

- `npm start`: Démarrer le serveur de développement
- `npm run build`: Compiler le code pour le préparer à la production
- `npm test`: Lancer les tests d'intégration

## Dépendances

- `create-react-app`
- `typescript`
- `react` + `react-dom`
- `react-router-dom`: navigation client
- `axios`: communication avec l'api
- `react-async-hook`: intégration de l'async dans react
- `clsx`: outil pour combiner des classes CSS
- `i18next`: gestion des traductions
- `date-fns`: gestion des dates

## Structure

- `public`: Fichiers statiques
- `src`: Code source du frontend
  - `account`: Gestion du compte utilisateur
  - `auth`: Authentification utilisateur
  - `carbure`: Point d'entrée de l'application
  - `common` + `common-v2`: Design system + outils pour structurer l'app
  - `companies`: Liste des sociétés enregistrées (admin)
  - `control-details`: Détails d'un lot contrôlé (admin + auditeur)
  - `controls`: Liste des lots à contrôler (admin + auditeur)
  - `dashboard`: Informations générales sur les déclarations (admin)
  - `doublecount`: Gestion des dossiers double comptage (admin + admin externe)
  - `lot-add`: Formulaire de création de lot
  - `lot-details`: Détails d'un lot existant
  - `settings`: Configuration d'une société
  - `stats`: Statistiques privées
  - `stock-details`: Détails d'un stock existant
  - `transactions`: Liste des transactions d'une société
