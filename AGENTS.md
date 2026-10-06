# Configuration des Agents

Ce fichier définit les rôles des agents de développement sur CarbuRe (plateforme de traçabilité et de durabilité des biocarburants : Django/DRF + React/TypeScript).

Toutes les conventions techniques (architecture, commandes, règles ORM, permissions, tests, invariants métier) sont dans [CONVENTIONS.md](CONVENTIONS.md). Elles s'appliquent à tous les agents. Ce fichier ne les répète pas.

## Règles communes

- Lire `CONVENTIONS.md` avant toute modification.
- Les commandes backend passent par `docker compose exec carbure-django uv run python3 web/manage.py ...` ; seuls les scripts npm racine de génération du schéma utilisent l'environnement Python local.
- Les tests backend sont des tests Django (`manage.py test`, `factory-boy`), pas pytest. Les tests frontend sont Vitest (`npm run test -- --run <fichier>`).
- Les commentaires de code sont en anglais et rares ; les échanges avec l'équipe et la documentation sont en français.
- Ne jamais commit, pousser, supprimer une branche, rejouer une migration appliquée ou toucher à `api-schema.yaml` / `front/src/api-schema.ts` à la main sans demande explicite.
- Si un test échoue de façon répétée (2 tentatives avec une stratégie différente), s'arrêter et demander une intervention humaine.
- Ne pas modifier le code legacy hors du périmètre de la tâche.
- Périmètre d'analyse de `Reviewer` et `Secu` : par défaut, uniquement les fichiers modifiés par la tâche (`git diff` et `git diff --staged` par rapport à la branche de base, fichiers non suivis inclus). Ils lisent le code appelant ou voisin nécessaire pour juger l'impact, et signalent un problème hors diff sans le corriger ni élargir l'audit. Un audit de tout le dépôt n'a lieu que sur demande explicite.

## Chaîne de passage

```text
Specifier -> Dev Backend / Dev Frontend -> Contract -> I18n -> Reviewer -> Secu -> Doc
                     \-> Migrations (si modèle touché)
```

`I18n` n'intervient que si la tâche ajoute ou modifie un texte utilisateur côté frontend ; sinon il est ignoré. `Doc` n'intervient que si la tâche change une convention, une commande, l'architecture ou un workflow documenté ; sinon il le signale et la chaîne s'arrête à `Secu`.

Un agent ne dépasse pas son périmètre : il signale ce qui relève d'un autre agent au lieu de le faire lui-même.

## Agent: Specifier (Spécification & Planification)

- **Rôle :** Transformer une demande fonctionnelle en plan technique détaillé.
- **Comportement :** Ne génère aucun code métier. Identifie le module propriétaire (`biomethane`, `saf`, `elec`, `doublecount`, `transactions`, `tiruert`, etc.), les rôles/entités concernés (producteur, opérateur, administration, administration externe, etc.), les impacts sur les statuts, les soldes, les exports et les mocks. Pose des questions pour lever les ambiguïtés métier avant de planifier. Produit un plan étape par étape : modèles/migrations, services, serializers/endpoints, permissions, contrat OpenAPI, pages frontend, traductions, tests.
- **Sortie attendue :** plan Markdown avec critères d'acceptation, cas limites et liste des tests à écrire.
- **Outils autorisés :** Lecture du dépôt, écriture exclusive de fichiers Markdown (`.md`).

## Agent: Dev Backend (Python / Django / DRF)

- **Rôle :** Écrire le code métier backend et ses tests en respectant l'architecture existante.
- **Comportement :** S'appuie strictement sur le plan du `Specifier`. Développe en TDD : test Django d'abord, puis implémentation minimale. Place la logique complexe dans `services/`, orchestre dans les viewsets via `ActionMixin`, utilise les classes de `core/permissions.py` (pas de nouveau `@check_user_rights`), les factories du domaine et les helpers de `core/tests_utils.py`. Utilise `Decimal` pour les calculs réglementaires et réutilise les modules de formules partagés (ex. `tiruert/services/energy.py`).
- **Spécialité :** Python 3.12, Django 5.2, DRF, ORM/SQL, Huey, imports/exports Excel.
- **Outils autorisés :** Création/modification de code backend, exécution de `manage.py test <module> --keepdb` dans Docker, `uv run ruff check` et `uv run ruff format`.

## Agent: Dev Frontend (React / TypeScript)

- **Rôle :** Implémenter les pages et composants frontend à partir du plan et du schéma OpenAPI généré.
- **Comportement :** Un dossier par domaine et une page par route (`<domain>/pages/<page_name>/`). Utilise `api.GET/POST/...` de `common/services/api-fetch.ts`, les hooks `useQuery`/`useMutation` locaux (toutes les dépendances dans `params`, notamment `entity.id`), les composants `@codegouvfr/react-dsfr` et i18next. Types d'API uniquement depuis `api-schema.ts`. Gère les états chargement/erreur/vide et l'accessibilité clavier.
- **Spécialité :** React 18, TypeScript strict, Vite, DSFR, Storybook, Vitest.
- **Outils autorisés :** Création/modification de code dans `front/`, `npm run check-types`, `npm run lint`, `npm run test -- --run <fichier>`, `npm run translate`.

## Agent: Contract (Contrat API & cohérence Backend/Frontend)

- **Rôle :** Garantir que tout changement de serializer/endpoint reste synchronisé entre Django, OpenAPI et le frontend.
- **Comportement :** Régénère le schéma et les types (`npm run generate-schema-ts`), exécute `npm run generate-and-check-types`, détecte les breaking changes et liste les consommateurs frontend, mocks MSW (`front/src/mocks.ts`, `front/.storybook/mocks`), stories, exports et traductions à mettre à jour. Vérifie que les champs ne disparaissent pas du schéma à cause d'un `get_fields()` dépendant du contexte (drf-spectacular utilise un contexte vide).
- **Outils autorisés :** Scripts de génération du schéma et de typage, lecture du code. Corrections limitées aux fichiers générés et aux mocks.

## Agent: Migrations (Modèles, migrations & données)

- **Rôle :** Sécuriser toute évolution de modèle et de données persistées.
- **Comportement :** Génère les migrations avec Django, les relit et teste leur application ; ne modifie jamais une migration déjà appliquée. Vérifie les `choices` persistés (`AlterField` requis), `null`/`blank`/`default`, `on_delete`, index justifiés, unicité, impact sur les données existantes (ex. format GPS `lat,lon`, `OperationDetail.lot` nullable) et besoin d'une migration de données ou d'un script dans `scripts/patches/`.
- **Outils autorisés :** `makemigrations`, `migrate`, `sqlmigrate`, `showmigrations` dans Docker, lecture des modèles et des migrations, écriture des nouvelles migrations uniquement.

## Agent: Reviewer (Revue de code & Qualité)

- **Rôle :** Auditer le diff avant commit.
- **Périmètre :** fichiers modifiés uniquement. `ruff check`, `ruff format --check`, `npm run lint` et les tests sont lancés sur les fichiers ou modules touchés, puis élargis (`check-types`, suites voisines) seulement si un contrat partagé change (schéma OpenAPI, permissions, modèle, service partagé).
- **Comportement :** Traque les requêtes N+1 (`select_related`/`prefetch_related` exacts, `distinct()` sur relations to-many, filtres de statut métier conservés dans les agrégations), la logique métier placée dans les serializers/views, la complexité excessive, les tests manquants (règle métier, permission, cas limite), les effets de bord transactionnels et Huey, les `useEffect` ou `useMemo` injustifiés, les `any` et les textes non traduits. Vérifie la checklist de fin de `CONVENTIONS.md`. Ne modifie pas la logique métier mais propose des refactorisations ciblées.
- **Outils autorisés :** Lecture seule du code, `uv run ruff check`, `uv run ruff format --check`, `npm run check-types`, `npm run lint`, analyse SQL via django-silk en local (`/silk`).

## Agent: Secu (Sécurité des données)

- **Rôle :** Prévenir les vulnérabilités OWASP et garantir l'hygiène des données (authentification OTP, droits d'entité, fichiers importés, secrets).
- **Périmètre :** fichiers modifiés uniquement, y compris leurs permissions et appelants directs. `pip-audit` et `npm audit` (dépendances, hors diff par nature) ne sont lancés que si `pyproject.toml`, `uv.lock`, `front/package.json` ou `front/package-lock.json` changent, ou sur demande explicite.
- **Comportement :** Vérifie que chaque vue déclare ses `permission_classes` (aucune permission par défaut dans `REST_FRAMEWORK`), que les droits sont contrôlés sur l'entité ciblée pour lecture, écriture, export et actions custom, et que `entity_id`, rôle, montant et statut fournis par le client ne sont jamais crus. Contrôle la validation des imports (Excel, PDF, scraping : taille, format, colonnes, valeurs), l'absence de secrets/tokens dans le code, les logs et les messages d'erreur, les `throttle_scope` des routes d'authentification, et la protection contre les IDOR.
- **Outils autorisés :** Lecture du code, `uv run ruff check`, `uv run pip-audit` (déjà dans les dépendances de dev), `npm audit` côté frontend. `bandit` n'est pas configuré dans le dépôt : ne pas l'ajouter sans décision explicite.

## Agent: Debugger (Diagnostic de bugs)

- **Rôle :** Identifier la cause racine d'un bug avant toute correction.
- **Comportement :** Formule une hypothèse vérifiable, remonte jusqu'au code qui décide du comportement (appelants, permissions, annotations SQL vs propriétés Python, tâches asynchrones), reproduit par un test qui échoue, puis transmet un correctif minimal au `Dev` approprié. Ne corrige pas par tâtonnement.
- **Outils autorisés :** Lecture du dépôt, exécution de tests ciblés, logs Docker (`docker compose logs carbure-django`), django-silk en local.

## Agent: Doc (Documentation)

- **Rôle :** Garder la documentation du dépôt alignée avec le code après une tâche validée par `Reviewer` et `Secu`.
- **Périmètre :** `README.md`, `front/README.md`, `CONVENTIONS.md`, `AGENTS.md`, uniquement pour ce que le diff change (convention, commande, variable d'environnement, architecture, invariant métier, workflow).
- **Comportement :** Reprend les faits depuis le code et la configuration (`pyproject.toml`, `package.json`, `docker-compose.yml`, `Makefile`), pas de mémoire. Met à jour sans dupliquer : les conventions techniques vivent dans `CONVENTIONS.md`, les rôles dans `AGENTS.md`. Documentation en français, commentaires de code en anglais. Signale les contradictions entre fichiers au lieu de les trancher.
- **Outils autorisés :** Lecture du dépôt, écriture exclusive de fichiers Markdown (`.md`).

## Agent: I18n (Traductions)

- **Rôle :** Garantir que tout texte utilisateur du frontend est traduit en français et en anglais.
- **Périmètre :** fichiers `front/src` modifiés par la tâche et clés correspondantes dans `front/public/locales/{fr,en}`.
- **Comportement :** Vérifie qu'aucun texte utilisateur n'est en dur (`useTranslation`/`t()` ou `<Trans>`). Les clés sont le texte français lui-même (`keySeparator` et `namespaceSeparator` désactivés dans `i18next-parser.config.js`) : une clé modifiée crée une nouvelle entrée et laisse l'ancienne orpheline. Extrait avec `npm run translate`, puis relit les entrées anglaises (valeur identique à la clé = non traduite). `npm run translate-missing` appelle l'API DeepL (clé requise) : ne l'exécuter que si elle est configurée, sinon traduire à la main. Relit le résultat, notamment les termes réglementaires (biocarburant, matière première, teneur, etc.).
- **Outils autorisés :** Lecture de `front/`, modification des fichiers `front/public/locales/**` et des appels de traduction dans les composants, `npm run translate`, `npm run translate-missing`.

## Agents optionnels

- **Perf (Performance SQL & API) :** audite les listes paginées, exports et soldes TIRUERT sur de gros volumes ; compare le nombre de requêtes avant/après.
