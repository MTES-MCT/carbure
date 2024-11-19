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
```

## Testing components

We decided to stop testing with react testing library because it didn't check the final rendering the user had. This is why these tests will gradually be migrated to Storybook and Chromatic, which offer a tool dedicated to the visual testing of components, corresponding to the user's final rendering.

### Workflow

During development, if certain components need to be tested, create a .stories.tsx file next to the component, and follow Storybook's documentation on how to create stories. Storybook's interface offers the option of launching visual tests for a component, which will launch the storybook build step, and then send the files to Chromatic.

You'll then need to go to Chromatic if the visual differences between the previous state and the current state of the component are no longer the same (see Chromatic documentation).

## Type safety with backend

## Type safety between frontend and backend

### Schema generation
The backend exposes its data structure through a YAML schema. This schema can be generated using the `generate-schema` command in the root package.json. This command will analyze the Python backend code and create a comprehensive OpenAPI schema that describes all available endpoints and their data types.

### Converting YAML to TypeScript
The `generate-schema-ts` command handles the full process of generating TypeScript types from the backend schema:
1. First, it generates the YAML schema from the Python code
2. Then, it processes this schema through a JavaScript script that can override specific schema information (particularly useful for enums where value names need to be used as variable names)
3. Finally, it uses the `openapi-typescript` library to convert the processed YAML schema into TypeScript type definitions

### Development workflow
During development, to ensure that backend changes haven't impacted the frontend type safety, you can run the `generate-and-check-types` command from the root directory. This command will:
1. Generate a fresh schema from the current backend state
2. Convert it to TypeScript types
3. Run the TypeScript compiler to check for any type errors that might have been introduced by the backend changes

This workflow ensures strong type safety between the frontend and backend, catching potential integration issues early in the development process.
