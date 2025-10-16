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
- Supporting files such as `types.ts`, `api.ts` can reside either in the page's folder or at the domain level.

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

We decided to stop testing with react testing library because it didn't check the final rendering the user had. This is why these tests will gradually be migrated to Storybook and Chromatic, which offer a tool dedicated to the visual testing of components, corresponding to the user's final rendering. In addition, we use vitest for unit testing.

### Workflow

Chromatic offers a free version with 5000 snapshots per month. For the moment, this offer is sufficient, and the significant cost of the paid version (£180/month) forces us to organise ourselves to avoid spending too much on captures.That is why, when developing features, the workflow is as follows :

- During development, if certain components need to be tested, create a .stories.tsx file next to the component, and follow Storybook's documentation on how to create stories (or check existing stories).
- Add tests for use cases that are worth testing.
- Once the tests match expectations and the branch work is complete, open a merge request, which will launch the storybook build and publish the screenshots on Chromatic. (This allows screenshots to be generated only at the time of the merge request and not during the development phase.)
- Check Chromatic to see if there are any differences in the screenshots. If so, accept/reject the screenshots depending on whether the result matches what was expected.
  
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

## Translations

Translation files are placed inside the `front/public/locales` folder. Each direct subfolder there should be named after a language code (ex: fr, en).
Inside those subfolders, there should be `.json` files, that contain a simple object with only key/value pairs.

To use translations in frontend code, you have two methods:

- using the react-i18next hook
- using the `<Trans>` component

You can find more details about their use in the [official documentation](https://react.i18next.com/guides/quick-start#translate-your-content).

If no namespace is specified when using those tools, the translations will be located in the file `{locale}/translation.json`.

You can prefill this file automatically by calling the command `npm run translate`: it will detect all the places where i18next is used in frontend code, and generate key/value pairs for each translation found.

Each new detected key will be added to the translation files of each locale, and then 3 operations must be done manually:

- On the french translation file, find each key where `count` was used ([https://www.i18next.com/translation-function/plurals]()), and adapt the value for each case (`{key}_one`, `{key}_many`, `{key}_other`)
- Once the french side is done, run the following command `npm run translate-missing`: it will find all the untranslated keys inside the english translation file, and translate them automatically using the free DeepL API
- To get better translations, you can specify a translation context to deepl by typing `npm run translate-missing -- "my context"`. "my context" should be a list of words or a sentence that explains what we're talking about in general in the French version.
- Double-check that the new english translations are correct before committing.

> [!NOTE]
> For the automatic translation to work, you'll need to add a DEEPL_API_KEY in your local .env
> You can either create your own key with your personal DeepL account (recommended), or use the shared one that you can find in Vaultwarden.
