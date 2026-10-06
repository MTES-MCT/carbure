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
- **Organisation frontend :** un dossier par domaine et une page dans `pages/<page_name>/` pour chaque route significative.
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

Le `Makefile` expose des raccourcis équivalents (`make test-backend`, `make test-frontend`, `make migrate`, `make lint-fix`, `make translate`).

## 4. Backend Python et Django

### Style Python

- Utiliser les annotations modernes compatibles avec Python 3.12 : `list[str]`, `dict[str, int]`, `str | None`.
- Préférer des types précis à `Any`. Si une donnée externe est inconnue, utiliser `object` ou `unknown` côté TypeScript et valider à la frontière.
- Respecter Ruff, la longueur de ligne configurée à 125 caractères et le tri d'imports `isort` via Ruff.
- Ne pas utiliser `print()` pour le diagnostic : utiliser le logging du projet.
- Préférer des fonctions courtes, déterministes et testables. Nommer les variables métier explicitement.
- Utiliser `Decimal` pour les calculs financiers, réglementaires ou nécessitant une précision décimale. Les littéraux décimaux utilisent un point, par exemple `Decimal("0.995")`.
- Centraliser les formules partagées plutôt que de recopier une formule dans un modèle, un service et une annotation ORM.

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
- Utiliser `ErrorResponse(status_code, error, data=None, message=None)` de `core.common` pour les erreurs métier lorsque le module le prévoit.
- Ne pas retirer un champ dans `get_fields()` uniquement selon le contexte si cela doit rester visible dans OpenAPI : drf-spectacular instancie les serializers avec un contexte vide. Préférer une représentation conditionnelle ou documenter explicitement le champ.
- Toute nouvelle route doit être protégée par l'authentification OTP (`is_verified()`) et les droits d'entité applicables. `EntityMiddleware` résout `request.entity` depuis le paramètre `entity_id` (POST form ou query string uniquement, pas le body JSON) : le transmettre côté frontend et vérifier les droits sur `request.entity` via les classes de permission.
- Vérifier les permissions sur les opérations de lecture, d'écriture, d'export et d'actions custom, pas seulement sur la route principale.

### Tests backend

- Le projet utilise les tests Django (`TestCase` et classes proches) et des factories `factory-boy` (dossiers `<app>/factories`) ; ne pas introduire pytest comme convention sans décision explicite.
- Réutiliser les helpers de `core/tests_utils.py` : `setup_current_user()` pour l'utilisateur OTP/droits d'entité, `PermissionTestMixin` pour tester les permissions d'un viewset, `FiltersActionTestMixin` pour les filtres.
- Ajouter un test pour chaque règle métier (avec docstring), branche de permission, cas limite et régression importante.
- Pour l'ORM, privilégier une base de test réelle (`TestCase` ou équivalent avec DB) plutôt qu'un mocking excessif.
- Utiliser des fixtures et factories lisibles ; éviter les données hardcodées lorsque la factory existe.
- Tester les effets de bord transactionnels, les exports, les tâches Huey et les changements de statut lorsque concernés.
- Après l'ajout d'une donnée dans une fixture partagée, revoir les assertions de compteurs et de sous-ensembles dans toute la classe de test.

## 5. Frontend React et TypeScript

### TypeScript et API

- Maintenir `strict: true`, `noUncheckedIndexedAccess: true` et `forceConsistentCasingInFileNames: true`.
- Ne pas utiliser `any` dans le nouveau code. Pour un JSON externe, partir de `unknown`, valider ou typer la frontière, puis propager un type précis.
- Les types de réponses et requêtes API viennent de `front/src/api-schema.ts`, généré depuis Django. Ne pas créer de doublon manuel pour un contrat existant.
- Pour toute modification backend, régénérer le schéma et les types, lancer `npm run generate-and-check-types`, puis corriger les consommateurs frontend.
- Utiliser `api.GET()`, `api.POST()`, `api.PATCH()`, etc. depuis `common/services/api-fetch.ts`. Ne pas appeler Axios directement pour l'API applicative.
- Respecter le serializer `toFormData()` configuré par le client pour les uploads et les payloads multipart.

### Données, état et effets

- Utiliser le hook local `useQuery`/`useMutation` fondé sur `react-async-hook` et le mécanisme d'invalidation existant pour le server state.
- Ne pas ajouter TanStack Query sans migration explicite du pattern partagé.
- Éviter `useEffect` pour un simple chargement de données ; utiliser le hook de requête existant. Réserver les effets aux effets externes réels.
- Inclure dans `params` toutes les valeurs dont dépend une requête, en particulier l'entité courante. Une closure avec `params: []` peut figer une ancienne valeur et empêcher le refetch.
- Ne pas utiliser `useMemo` ou `useCallback` par réflexe. Les introduire uniquement lorsqu'un calcul ou une identité de référence mesurable le justifie.
- Séparer autant que possible la présentation pure, la logique de formulaire et la logique métier/API.

### Structure et interface

- Respecter les dossiers par domaine et par page ; réutiliser `common/` avant de créer un composant global.
- Utiliser les composants et tokens de `@codegouvfr/react-dsfr` avant un style local.
- Utiliser i18next (`useTranslation` ou `Trans`) pour tout texte utilisateur. Les clés vivent dans `front/public/locales/{fr,en}` : les extraire avec `npm run translate` (depuis `front/`) puis compléter l'anglais avec `npm run translate-missing` (DeepL) ou à la main.
- Utiliser les icônes et patterns de navigation déjà présents dans le design system ; conserver l'accessibilité clavier, les labels et les états chargement/erreur/vide.
- Ne pas mettre la logique d'autorisation uniquement dans l'UI : l'API reste l'autorité.

### Tests frontend

- Utiliser Vitest pour les tests unitaires et Storybook/Chromatic pour les composants visuels.
- Tester les comportements visibles, les erreurs réseau, les changements de contexte d'entité et les états loading/empty/error.
- Mettre à jour les stories lorsque l'UI réutilisable ou ses états changent.
- Vérifier `npm run check-types`, `npm run lint` et le test ciblé avant une validation plus large.

## 6. Sécurité, données externes et asynchronisme

- Ne jamais exposer une variable d'environnement, un secret, une clé API, un token ou une donnée sensible dans le code frontend, les logs, les exports ou les messages d'erreur.
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

## 8. Checklist de fin

- [ ] Le comportement a été tracé jusqu'au code qui le décide.
- [ ] Les permissions, entités, statuts et données sensibles ont été vérifiés.
- [ ] Le chemin ORM ne crée pas de N+1 et conserve les filtres métier.
- [ ] Les types OpenAPI/TypeScript sont régénérés si le contrat a changé.
- [ ] Les tests ciblés couvrent le changement et ses cas limites.
- [ ] Les migrations sont nouvelles, relues et testables ; aucune migration existante n'a été réécrite.
- [ ] Ruff, typecheck, lint ou test frontend pertinent a été exécuté.
- [ ] Le diff reste limité à la tâche et ne contient ni secret, ni debug, ni fichier généré oublié.