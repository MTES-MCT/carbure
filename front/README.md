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

### Overview

The project is structured to facilitate modular development, ensuring that each domain is clearly separated and maintainable. The architecture guidelines are as follows:

### folder definitions

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

### Domain-Specific Structure

- **Each domain** has its own folder (e.g., `saf`, `biofuels`, `elec`).
- Within each domain, there is a `pages/` directory, which contains subdirectories for each page within the domain. **Note:** Each folder in `pages/` corresponds to a specific route.

#### Page Structure

- Each page is represented by an `index.tsx` file within its respective folder.
- Supporting files such as `types.ts`, `api.ts`, and test files (`*.spec.tsx`) can reside either in the page's folder or at the domain level.

### Shared Components

- Components that are shared across multiple pages within the same domain are stored in the domain's `components/` directory.
- Components that are shared across multiple domains are stored in `common/components/`.

### Common Files

- Similar to components, shared `types.ts` and `api.ts` files are also placed in `common/`, adhering to the same organizational principles.

### Design System

- Components related to the design system of Carbure are stored in the `common/ui/` directory.

## Example Folder Structure

```plaintext
saf/
biofuels/
elec/
  pages/
    cpo/
      charge-points/
        index.tsx
        registration/
        meter-readings/
    admin/
      audit/
        index.tsx
        types.ts
        charge-points/
          admin-audit-charge-points.spec.tsx 
          index.tsx
        meter-readings/
          index.tsx
      certificates/
        transfer-certificates/
          index.tsx
          types.ts
          api.ts
        provision-certificates/
          index.tsx
          types.ts
          api.ts
        index.tsx
        types.ts
  components/
    admin-audit-sample/
      application-generation.tsx
      sample-map.tsx

common/
  components/
  ui/
