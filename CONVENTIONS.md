# CONVENTIONS.md

## 1. Objet et règles de lecture

Ce fichier est la référence agnostique des agents de développement (OpenCode, T3, Cursor, VS Code, Claude Code, Codex, etc.) pour CarbuRe. Il décrit les conventions à respecter lors d'une lecture, d'une modification ou d'une création de code.

Ordre de priorité :

1. Les exigences de sécurité et les contraintes explicites de la tâche.
2. Le code existant et ses tests lorsqu'ils décrivent un comportement métier déjà supporté.
3. Ce document et les fichiers de configuration du dépôt.
4. Les préférences de l'agent.

Une règle nouvelle doit être appliquée au code créé ou modifié. Elle ne justifie pas une refactorisation générale du legacy sans demande explicite.

Avant toute modification, l'agent doit :

- identifier le module propriétaire du comportement ;
- lire le code qui décide réellement du comportement, ses appelants et le test voisin le plus pertinent ;
- formuler une hypothèse vérifiable sur le bug ou le changement attendu ;
- rechercher les permissions, les effets de bord, les transactions, les tâches asynchrones et les performances SQL concernés ;
- choisir la vérification la moins coûteuse qui peut invalider cette hypothèse.

Après toute modification :

- lancer un test, un typecheck ou un lint ciblé ;
- élargir la vérification lorsque le changement touche un contrat partagé ;
- ne pas considérer la tâche terminée si la validation pertinente n'a pas été exécutée ou si son impossibilité n'est pas signalée.

Les commentaires ajoutés au code sont en anglais et restent rares : ils expliquent uniquement une décision non évidente. La documentation destinée aux humains peut être en français.

## 2. Vision et architecture

- **Produit :** CarbuRe, plateforme de traçabilité et de durabilité des biocarburants.
- **Backend :** Python `>= 3.12`, Django 5.2, Django REST Framework, drf-spectacular, MySQL 8, Redis et Huey (S3 mocké en local via `carbure-s3mock`).
- **Frontend :** React 18, TypeScript strict, Vite, `openapi-fetch`, `react-async-hook`, React Router, i18next et `@codegouvfr/react-dsfr`.
- **Déploiement local :** services conteneurisés via Docker Compose.
- **Organisation backend :** une app Django par domaine métier (`biomethane`, `saf`, `elec`, `doublecount`, `transactions`, etc.).
- **Organisation frontend :** un dossier par domaine. Le code récent place chaque route dans `pages/<page_name>/` selon la section 5. Le legacy conserve son arborescence.
- **Architecture métier :** les vues, viewsets et serializers orchestrent ; les règles métier complexes vivent dans `services/` et les modules spécialisés.
- **Contrat API :** Django produit le schéma OpenAPI ; `front/src/api-schema.ts` est généré et ne doit pas être édité à la main.

Ne pas introduire une nouvelle librairie ou une nouvelle abstraction lorsque le dépôt possède déjà un helper ou un pattern équivalent.

## 3. Workflow et commandes

Les commandes applicatives backend s'exécutent dans Docker Compose. Utiliser le service réel du projet et `uv` :

```bash
docker compose exec carbure-django uv run python3 web/manage.py <commande>
```

Commandes usuelles :

```bash
# Démarrer l'environnement
docker compose up

# Tests Django
docker compose exec carbure-django uv run python3 web/manage.py test <chemin.de.test> --keepdb

# Migrations
docker compose exec carbure-django uv run python3 web/manage.py makemigrations
docker compose exec carbure-django uv run python3 web/manage.py migrate

# Backend lint (CI : `ruff check` + `ruff format --check`)
uv run ruff check web
uv run ruff format web

# Schéma OpenAPI et types TypeScript (depuis la racine du dépôt)
npm run generate-schema-ts
npm run generate-and-check-types

# Frontend
cd front
npm run check-types
npm run lint
npm run test -- --run <fichier-de-test>

# Traductions
npm run translate
npm run translate-missing
```

Les scripts npm racine (`generate-schema`, `generate-schema-ts`, `generate-and-check-types`) appellent `python web/manage.py` avec l'environnement Python local (`.venv` géré par `uv`) car `api-schema.yaml` est écrit à la racine, non montée dans le conteneur. C'est la seule exception à la règle Docker ci-dessus ; le hook pre-push exécute `npm run generate-and-check-types`.

Ne pas appeler directement `manage.py` avec l'interpréteur local pour une vérification qui dépend de l'environnement applicatif (base, Redis, S3). Ne pas utiliser `docker compose run` pour un test ciblé si l'image ou l'entrypoint ne garantit pas la présence de `uv`. Si `docker compose exec` échoue dans un terminal sandboxé (`~/.docker/config.json: operation not permitted`), relancer hors sandbox.

Le `Makefile` expose des raccourcis équivalents (`make test-backend`, `make test-frontend`, `make migrate`, `make lint-fix`, `make translate`). Les commandes de cette section restent la référence.

### Environnement local

- Application : `http://carbure.local:8090`. Les scripts `uv` locaux lisent `UV_ENV_FILE=.env`.
- Connexion : `http://carbure.local:8090/auth/login`. Après le mot de passe, un code à 6 chiffres est exigé. Il est stocké sur `EmailDevice`, pas dans une boîte mail. Le lire juste après la soumission du formulaire :

```bash
docker compose exec carbure-django uv run python3 web/manage.py shell -c "
from django_otp.plugins.otp_email.models import EmailDevice
d = EmailDevice.objects.filter(user__email='user@carbure.local').order_by('-id').first()
print(d.token)
"
```

- L'écran d'accueil dépend des seeds déjà lancés. Retrouver la société par son nom, puis prendre son id pour ouvrir `/org/<id>/...`.

### Données de démo

- `docker compose exec carbure-django uv run python3 web/manage.py create_sample_data <module>` (raccourci : `make seed app=<module>`) appelle `web/<module>/factories/sample_data.py`.
- Comptes communs dans `web/core/factories/sample_data.py` : `admin@carbure.local` et `user@carbure.local`, mot de passe `password`, créés seulement s'ils n'existent pas.

### Git

- Branche : `feature/<numéro-issue>-<slug>` (ex. `feature/2098-dreal-dashboard-recap`).
- Commits en anglais, format conventionnel (`feat(biomethane): …`, `fix(tiruert): …`).
- Description de MR en français : objectif, modélisation, subtilités métier.
- Pas de trailer `Co-authored-by` sans demande explicite.

### Scripts one-shot

- Un seul fichier, périmètre minimal. Pas de tests ni de refactoring autour.
- Option `--dry-run` quand c'est pertinent (cf. `import_biomethane_producers`).
- Fichiers SQL de debug dans `web/<module>/sql/`, hors commit sauf demande.

## 4. Backend Python et Django

### Organisation d'une app

| Couche | Rôle |
|--------|------|
| `models/` | Modèles, choices, `translation_model_key` si les libellés partent dans `backend_inputs` |
| `services/` | Logique métier, calculs, requêtes complexes |
| `serializers/` | Validation entrée et sortie API |
| `filters/` | FilterSet django-filter et mixins réutilisables |
| `views/` | ViewSets fins, qui délèguent aux services et serializers |
| `views/.../mixins/` | Actions transverses (export Excel, permissions) |
| `tests/` | Miroir de la structure (`tests/services/`, `tests/views/`) |

### Style Python

- Utiliser les annotations modernes compatibles avec Python 3.12 : `list[str]`, `dict[str, int]`, `str | None`.
- Préférer des types précis à `Any`. Si une donnée externe est inconnue, utiliser `object` ou `unknown` côté TypeScript et valider à la frontière.
- Respecter Ruff, la longueur de ligne configurée à 125 caractères et le tri d'imports `isort` via Ruff.
- Ne pas utiliser `print()` pour le diagnostic : utiliser le logging du projet.
- Préférer des fonctions courtes, déterministes et testables. Nommer les variables métier explicitement.
- Utiliser `Decimal` pour les calculs financiers, réglementaires ou nécessitant une précision décimale. Les littéraux décimaux utilisent un point, par exemple `Decimal("0.995")`.
- Centraliser les formules partagées plutôt que de recopier une formule dans un modèle, un service et une annotation ORM. Quand la même formule existe en Python et en SQL, exposer les deux dans le module partagé (fonction Python et expression ORM), comme `tiruert/services/energy.py` (`energy_mj` / `energy_mj_expression`).

### Modèles et migrations

- Pour un nouveau `CharField` ou `TextField`, ne pas utiliser `null=True` pour représenter une chaîne vide : préférer `blank=True, default=""`. Une exception doit être motivée par une contrainte d'intégration ou la sémantique réelle de `NULL`.
- Définir `null=True` uniquement lorsque l'absence est différente d'une valeur vide et choisir explicitement `blank`, `default` et `on_delete`.
- Ajouter les index justifiés par les filtres, jointures et tris fréquents ; ne pas indexer mécaniquement chaque champ.
- Vérifier les contraintes d'unicité, les choix persistés, les suppressions en cascade et les implications historiques avant de modifier un modèle.
- Ne jamais modifier une migration déjà appliquée. Modifier le modèle, générer une nouvelle migration avec Django, la relire et tester son application.
- Toute modification de `choices` doit prendre en compte l'état des migrations Django : une nouvelle valeur peut nécessiter une migration `AlterField`.
- Préserver les noms de tables et de colonnes historiques sauf migration de données explicitement planifiée.

### ORM et performances

- Examiner le SQL et le nombre de requêtes dès qu'un queryset est utilisé dans une boucle, une pagination ou une sérialisation.
- Utiliser `select_related()` pour les relations ForeignKey et OneToOne nécessaires, et `prefetch_related()` pour les relations inverses et ManyToMany.
- Ne pas ajouter un preload aveuglément : vérifier que le chemin relationnel correspond exactement à l'accès réel, notamment pour les objets optionnels.
- Préférer les annotations, agrégations et sous-requêtes SQL lorsque le calcul peut être fait par la base, tout en conservant exactement les filtres métier requis.
- Conserver les filtres de statut métier dans les agrégations.
- Avec un filtre custom sur une relation to-many, vérifier si `distinct()` est nécessaire ; remplacer un `MultipleChoiceFilter` peut supprimer implicitement cette déduplication.
- Ne pas modifier le queryset d'un manager par défaut pour cacher globalement des lignes si ce manager est utilisé par des sous-requêtes ou des related managers.
- Mesurer les cas volumineux et éviter les listes Python de données qui peuvent être traitées par le SGBD.

### API Django REST Framework

- Lire le modèle, le serializer, la vue/viewset et le test d'endpoint avant de modifier un contrat.
- Utiliser les serializers `Base*` pour le partage, puis des serializers explicites `*Add` et `*Update` lorsque les contraintes diffèrent.
- Mettre la logique métier complexe dans un service, pas dans `Serializer.validate()` ou une view volumineuse.
- Aucune permission par défaut n'est définie dans `REST_FRAMEWORK` : chaque vue doit déclarer explicitement ses `permission_classes` (ou `@permission_classes` pour un `api_view`).
- Pour tout nouvel endpoint DRF, utiliser les classes de `core/permissions.py` : `IsVerified` (OTP vérifié), `UserRightsFactory(role=..., entity_type=...)`, `HasEntityReadRights`, `HasEntityWriteRights`, `AdminRightsFactory(allow_external=..., allow_role=...)`, ou une classe dérivée propre au domaine (ex. `biomethane/permissions.py`). Ne pas introduire `@check_user_rights` sur du nouveau code.
- `@check_user_rights` (`core/decorators.py`) est un mécanisme legacy encore très présent (notamment `elec/`) : le conserver uniquement lors de la maintenance d'un endpoint existant qui l'utilise déjà, sans étendre son usage.
- Pour une action de viewset, suivre le pattern local `ActionMixin`, déclarer explicitement ses permissions et vérifier les droits sur l'entité ciblée.
- Réutiliser les mixins déjà présents : `RetrieveSingleObjectMixin`, `ListWithObjectPermissionsMixin`, `FiltersActionFactory`. Les permissions d'un viewset passent par le helper du module (`get_biomethane_permissions()` ou équivalent), pas par une liste recopiée.
- Filtrage société / producteur : `EntityProducerFilter` et `EntityProducerYearFilter` (`web/biomethane/filters/mixins.py`) quand l'écran distingue l'entité connectée et le producteur consulté.
- Documenter les paramètres de query (`entity_id`, `producer_id`, `year`) avec `@extend_schema`.
- Utiliser `ErrorResponse(status_code, error, data=None, message=None)` de `core.common` pour les erreurs métier lorsque le module le prévoit.
- Ne pas retirer un champ dans `get_fields()` uniquement selon le contexte si cela doit rester visible dans OpenAPI : drf-spectacular instancie les serializers avec un contexte vide. Préférer une représentation conditionnelle ou documenter explicitement le champ.
- Toute nouvelle route doit être protégée par l'authentification OTP (`is_verified()`) et les droits d'entité applicables. `EntityMiddleware` résout `request.entity` depuis le paramètre `entity_id` (POST form ou query string uniquement, pas le body JSON) : le transmettre côté frontend et vérifier les droits sur `request.entity` via les classes de permission.
- Vérifier les permissions sur les opérations de lecture, d'écriture, d'export et d'actions custom, pas seulement sur la route principale.

### Tests backend

- Le projet utilise les tests Django (`TestCase` et classes proches) et des factories `factory-boy` (dossiers `<app>/factories`) ; ne pas introduire pytest comme convention sans décision explicite.
- Réutiliser les helpers de `core/tests_utils.py` : `setup_current_user()` pour l'utilisateur OTP/droits d'entité, `PermissionTestMixin` pour tester les permissions d'un viewset, `FiltersActionTestMixin` pour les filtres.
- Construire les URL avec `reverse()` et affirmer `status.HTTP_*`.
- Permissions d'une vue : `PermissionTestMixin.assertViewPermissions`, sur le modèle de `web/biomethane/tests/test_permissions.py`. Pas de boucle manuelle sur `get_permissions`.
- Ajouter un test pour chaque règle métier (avec docstring), branche de permission, cas limite et régression importante.
- Pour l'ORM, privilégier une base de test réelle (`TestCase` ou équivalent avec DB) plutôt qu'un mocking excessif.
- Utiliser des fixtures et factories lisibles ; éviter les données hardcodées lorsque la factory existe.
- Tester les effets de bord transactionnels, les exports, les tâches Huey et les changements de statut lorsque concernés.
- Après l'ajout d'une donnée dans une fixture partagée, revoir les assertions de compteurs et de sous-ensembles dans toute la classe de test.

## 5. Frontend React et TypeScript

Le code récent suit la structure ci-dessous. Le legacy (appels Axios, fichiers `*.spec.*`, pages qui ne découpent pas `api.ts` / `*.hooks.tsx`) reste en place : on ne le migre pas pour l'aligner.

### TypeScript et API

- Maintenir `strict: true`, `noUncheckedIndexedAccess: true` et `forceConsistentCasingInFileNames: true`.
- Ne pas introduire `any` dans le code récent. Pour un JSON externe, partir de `unknown`, valider ou typer la frontière, puis propager un type précis. Le `any` déjà présent dans le code partagé (notamment `common/hooks/async.ts`) ne se corrige pas au passage.
- Les schémas de réponse et de requête passent par `apiTypes` (`common/services/api-fetch.types`). Les types de filtres OpenAPI (`PathsApi…`) s'importent depuis `api-schema` et se réexportent depuis le `types.ts` de la page ou du domaine. Ne pas recréer à la main un contrat déjà généré. Ne pas éditer `front/src/api-schema.ts`.
- Pour toute modification backend, régénérer le schéma et les types avec `npm run generate-and-check-types` (racine du dépôt), puis corriger les consommateurs frontend.
- Nouveau code : `api.GET()`, `api.POST()`, `api.PATCH()`, etc. et `download()` depuis `common/services/api-fetch.ts`. Un fichier qui appelle déjà Axios le conserve.
- Respecter le serializer `toFormData()` configuré par le client pour les uploads et les payloads multipart.

### Données, état et effets

- Utiliser `useQuery` / `useMutation` de `common/hooks/async` (fondés sur `react-async-hook`) et l'invalidation existante (`invalidates: [key]`).
- Ne pas ajouter TanStack Query sans migration explicite du pattern partagé.
- Éviter `useEffect` pour un chargement de données. Réserver les effets aux effets externes réels.
- `useQuery` ne relance la requête que si `params` change.
  - Page liste avec `useQueryBuilder` : `params: [query]`. Le builder injecte déjà `entity_id` de la société connectée (`useEntity()`).
  - Autre page : chaque argument de la fonction API figure dans `params`. `useEntity().id` est la société connectée (droits, query `entity_id`). `useSelectedEntity().selectedEntityId` est une société consultée par un admin (souvent `producer_id`) ; l'inclure quand l'écran dépend de cette sélection. Hors vue admin, ce hook vaut `undefined`.
- Ne pas utiliser `useMemo` ou `useCallback` par réflexe. Les introduire uniquement lorsqu'un calcul ou une identité de référence mesurable le justifie.
- Séparer la composition de page, les hooks (requêtes, colonnes, filtres) et les appels HTTP (`api.ts`).

### Structure d'une page récente

Hiérarchie des routes :

```
common/index.tsx          → /org/:entity/*
  <module>/index.tsx      → ex. accounting/*, settings/*
  <module>/routes.tsx     → ex. biomethane/* (module avec sous-routes)
    lazy(() => import("…/pages/<page>"))
```

- URLs typées : `ROUTE_URLS` (`common/utils/routes.ts`) et `useRoutes()` (injecte `entity.id`).
- Titre de navigation : `usePrivateNavigation(title)` dans la page ou le layout.
- Redirections d'année ou de secteur : `<Navigate replace>` ou un composant dédié dans le fichier de routes.
- Providers de contexte sur le `element` de la `<Route>`, pas recopiés dans chaque page.

Arborescence cible d'une page liste :

```
<domaine>/pages/<page>/
  index.ts              → export default (lazy import)
  <page>.tsx            → composition UI
  <page>.hooks.tsx      → queries, mutations, colonnes, filtres
  api.ts                → appels HTTP typés
  types.ts              → alias apiTypes, QueryBuilder, filtres
  utils.ts              → formatters purs (optionnel)
  components/           → sous-composants (+ *.hooks.tsx)
  pages/<sous-page>/    → détail, formulaire (optionnel)
```

- Types partagés par plusieurs pages du domaine : `<domaine>/types.ts`.
- API partagée : `<domaine>/api/<ressource>.ts` (ex. `accounting/api/biofuels/operations.ts`).
- Un formulaire ou un dialogue reprend le même découpage `api.ts` / `*.hooks.tsx` / composant, sans le squelette tableau.

`types.ts` d'une page liste :

```typescript
import { apiTypes } from "common/services/api-fetch.types"
import { PathsApiModuleItemsFiltersGetParametersQueryFilter as ItemFilter } from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"

export type Item = apiTypes["Item"]
export type ItemQueryBuilder = QueryBuilder<never, ItemOrder[]>
export type ItemQuery = ItemQueryBuilder["query"]
export { ItemFilter }
```

Hooks d'une liste :

- `useXxxQuery` : `useQueryBuilder` + `useQuery(fn, { key, params })`.
- `useGetFilterOptions` : labels i18n, normalizers, appel `/filters/`.
- `useXxxColumns` : `Column<T>[]` pour `table2`.
- `useXxxMutation` : `useMutation(fn, { invalidates: [key], onSuccess })`.

Squelette d'une liste : `ActionBar` (recherche, actions, `ExportButton`), `FilterMultiSelect2`, `Table`, `Pagination`, et `HashRoute` pour un détail qui ne change pas de route. Ouverture : `hash: "#/<path>"`. Fermeture : `navigate({ search: location.search, hash: "#" })`, pour conserver les filtres dans l'URL. Contenu : `Portal` + `Dialog` (`dialog2`), `useHashMatch`.

Emplacement des composants :

- `<domaine>/components/` : partagé entre les pages du domaine.
- `common/components/` : transverse (`button2`, `table2`, `dialog2`, `notice`, `scaffold`).
- `common/molecules/` : blocs composés (`FilterMultiSelect2`, `RecapQuantity`, `BetaPage`).
- `@codegouvfr/react-dsfr` : primitives (Badge, Alert, Select), avant un style local.

L'affichage conditionnel (droits, règles d'arrêté) vit dans un hook ou un provider du domaine. Conserver l'accessibilité clavier, les labels et les états chargement, erreur et vide.

### Textes et traductions

- Tout texte d'interface passe par `useTranslation()` ou `Trans`. La clé est le français, dans le namespace par défaut (`translation`). Ne pas créer de namespace.
- `{ ns: "…" }` uniquement pour un référentiel déjà catalogué : `biofuels`, `feedstocks`, `countries`, `fields`, `errors`, `backend_inputs`.
- `front/public/locales/{fr,en}/backend_inputs.json` est produit par `export_backend_inputs`. Ne pas l'éditer à la main. Un libellé manquant se corrige en relançant cette commande.
- Les clés sont le texte français (`keySeparator` et `namespaceSeparator` désactivés dans `i18next-parser.config.js`). Une clé modifiée crée une nouvelle entrée et laisse l'ancienne orpheline. En anglais, une valeur identique à la clé n'est pas traduite.
- `npm run translate-missing` appelle DeepL lorsque la clé est configurée. Sinon, traduire à la main et relire les termes réglementaires (biocarburant, matière première, teneur, etc.).
- Le code récent écrit `t("…")`. L'extraction et l'anglais relèvent de l'agent I18n.

### Tests frontend

- Tests unitaires du code récent : Vitest, fichiers `*.test.ts` ou `*.test.tsx`. Les fichiers `*.spec.*` sont du legacy : ne pas en créer, ne pas les typer, ne pas les lancer pour valider une tâche. `front/tsconfig.json` les exclut déjà de `check-types`.
- Stories `*.stories.tsx` lorsque l'UI réutilisable ou ses états changent. Storybook et Chromatic servent au visuel.
- Couvrir les comportements visibles, les erreurs réseau, le changement d'entité et les états loading, empty et error.
- Avant une validation plus large : `npm run check-types`, `npm run lint`, et `npm run test -- --run <fichier>`.

## 6. Sécurité, données externes et asynchronisme

- Ne jamais exposer une variable d'environnement, un secret, une clé API, un token ou une donnée sensible dans le code frontend, les logs, les exports ou les messages d'erreur.
- Masquer un contrôle dans l'interface ne remplace pas le contrôle d'accès de l'API.
- Isoler et tester l'assainissement des fichiers importés, PDF, feuilles Excel et données scrappées. Valider taille, format, encodage, colonnes, identifiants et valeurs avant toute écriture.
- Ne jamais faire confiance à un `entity_id`, rôle, montant, statut ou indicateur fourni par le client ; recalculer et vérifier côté serveur.
- Préserver les contrôles d'accès existants (`IsVerified`, classes de `core/permissions.py`, `@check_user_rights` legacy). Toute simplification qui les contourne est une régression de sécurité.
- Les endpoints d'authentification et de création de compte utilisent un `throttle_scope` dédié (`otp`, `auth-anon`, `add-company`) : le conserver sur toute route similaire.
- Encadrer les opérations multi-écritures par la transaction adaptée. Déterminer explicitement si une tâche Huey doit être synchrone, idempotente ou rejouable.
- Pour une correction métier qui doit être atomique avec la requête initiale, ne pas la déplacer dans une tâche asynchrone sans analyser les fenêtres d'incohérence.

## 7. Invariants métier et pièges connus

- Les calculs de solde doivent exclure les statuts non actifs et conserver les filtres de période, d'entité et de domaine.
- Les corrections GHG d'un lot doivent être prises en compte à la fois dans les propriétés Python et dans les annotations SQL.
- Les calculs de teneur respectent la précision métier : sommer par opération, tronquer au niveau prévu, puis agréger ; ne pas déplacer la troncature au mauvais niveau.
- Les formules d'énergie et d'émissions doivent réutiliser le module de formules partagé lorsqu'il existe.
- Dans les imports Excel, filtrer les lignes préremplies sans volume avant validation et agréger les volumes d'un même lot lorsque plusieurs groupes peuvent le référencer.
- Pour les regroupements d'import, vérifier toutes les dimensions métier de la clé (type, catégorie douanière, biocarburant, entité créditée) et ne pas déduire une donnée du mauvais modèle.
- Les coordonnées GPS utilisent le format `lat,lon`. Un changement de format nécessite d'analyser les données déjà stockées, pas seulement le code d'écriture.
- Pour un endpoint ou un serializer qui change, vérifier le schéma OpenAPI, les exports, les mocks MSW (`front/src/mocks.ts`, `front/.storybook/mocks`), les stories et les traductions impactés.
- Le module `tiruert/services/energy.py` centralise les formules d'énergie (`energy_mj`) et d'émissions évitées (`avoided_emissions_tco2`) en Python et ORM.
- Pour les imports Excel TIRUERT, grouper les lignes à partir de `CarbureLot` (`lot.feedstock.category`, `lot.biofuel`) et non du dernier `OperationDetail`.

## 8. Filières

Lire la sous-section du module avant de le modifier. Elle ne remplace pas le code ni les tests du module.

### Hydrogène

- Entité : `Entity.HRS` (opérateur de station). Admin : `EXTERNAL_ADMIN` + `ExternalAdminRights.H2` (`HasH2AdminRights`), voit les sociétés HRS. Lecture HRS : `HasHRSRights`. Écriture admin ou lecture-écriture : `HasHRSWriteRights`.
- Périmètre : un HRS voit ses stations (`created_by = request.entity`). Un admin H2 voit toutes les stations, en lecture seule.
- `H2Station` hérite de `Site`. `access_type` : PUBLIC ou PRIVATE. `distributed_pressure` est multi-valeurs (350 et 700 bars, `JSONChoiceField`) : une station peut distribuer plusieurs pressions. `has_personal_vehicle_connector` : bool. `has_compliant_measuring_instruments` : bool ou null (déclaration de conformité décret 2001-387, optionnelle). `is_renewable_hydrogen` : bool, défaut `False`. `storage_capacity` et `distribution_capacity` : entiers, unités encore à préciser.
- `H2ActionDetails` : OneToOne sur `Action` (`lot_id`, `producer`, `batch_id`), exposé en `extension`.
- API : `H2StationViewSet` (CRUD, `entity_id` en query). Front : `front/src/h2/pages/stations/`, page unique opérateur et admin. L'écriture est masquée via `canWriteStations`.
- Tests : `docker compose exec carbure-django uv run python3 web/manage.py test h2 --keepdb`.

### Biométhane

- `BiomethaneContract` : producteur, `tariff_reference` (2011, 2020, 2021, 2023). `TARIFF_RULE_1` = [2011, 2020], `TARIFF_RULE_2` = [2021, 2023] pour les règles de contrat (Cmax, etc.). Ces groupes sont distincts des régimes de coefficients d'intrants (ils peuvent diverger, ex. AT_2011 et AT_2020_PLUS).
- `BiomethaneSupplyPlan` / `BiomethaneSupplyInput` : plan d'approvisionnement par producteur et par année. `MatierePremiere` (`core.models`) est le catalogue d'intrants, lié via `feedstock`. `BiomethaneFeedstockTariffCoefficient` : `(feedstock, regime_key)` vers un coefficient (P1, P2, P3, P, PEFF).
- Proportions P1, P2, etc. : calculées sur le tonnage de matière brute. Convertir le sec vers le brut via le ratio si besoin. Le cas Peff local utilise `collection_type = LOCAL` sur le supply input. Le coefficient effectif d'un intrant vient du régime dérivé du `tariff_reference` du contrat producteur.
- API plan d'approvisionnement : `BiomethaneSupplyInputViewSet` (mixins Excel, `FiltersActionFactory`). Filtres : `entity_id` pour un producteur, `entity_id` + `producer_id` pour une DREAL. Service : `biomethane/services/supply_plan/`. SQL de debug : `web/biomethane/sql/`.
- Front : `front/src/biomethane/pages/supply-plan/`. L'affichage selon l'arrêté passe par un hook et `@codegouvfr/react-dsfr/Alert`. Permissions d'écran : `useBiomethanePermissions()`.
- Import du référentiel : commandes dans `web/biomethane/management/commands/`, Excel dans `web/biomethane/fixtures/`, `--dry-run=true` par défaut. Vérifier qu'une matière première existe par nom avant de la créer.
- Libellés de champs : `docker compose exec carbure-django uv run python3 web/manage.py export_backend_inputs --modules=biomethane --locales=fr,en`.
- Tests : `docker compose exec carbure-django uv run python3 web/manage.py test biomethane --keepdb`.

### Traçabilité

Avant de modifier ce module, lire `web/traceability/README.md`.

Après toute évolution de comportement (modèle, handler, colonnes Excel, serializer d'import, permissions, composition front, nouvelle filière), mettre à jour la doc dans le même changement.

- Personnalisation filière : `web/traceability/README.md`.
- Colonnes Excel : `web/traceability/docs/excel.md`.
- Documenter, si ça change : où vit la donnée (noyau `Action` ou table d'extension), la `key` Excel, le serializer filière, le lookup.
- Un rename interne, un test, du formatage ou un correctif qui ne change pas le contrat ne mettent pas la doc à jour.
- Le README reste la source de vérité : ne pas recopier l'architecture ailleurs.

## 9. Checklist de fin

- [ ] Le comportement a été tracé jusqu'au code qui le décide.
- [ ] Les permissions, entités, statuts et données sensibles ont été vérifiés.
- [ ] Le chemin ORM ne crée pas de N+1 et conserve les filtres métier.
- [ ] Les types OpenAPI/TypeScript sont régénérés si le contrat a changé.
- [ ] Les tests ciblés couvrent le changement et ses cas limites.
- [ ] Les migrations sont nouvelles, relues et testables ; aucune migration existante n'a été réécrite.
- [ ] Ruff, typecheck, lint ou test frontend pertinent a été exécuté (`npm run check-types`, `npm run lint`, `npm run test -- --run <fichier>`).
- [ ] Le code frontend récent suit la structure cible ; le legacy (Axios, `*.spec.*`) n'a pas été migré.
- [ ] Les textes d'interface passent par `t()` ; `backend_inputs.json` n'a pas été édité à la main.
- [ ] Le diff reste limité à la tâche et ne contient ni secret, ni debug, ni fichier généré oublié.