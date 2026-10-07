# Configuration des Agents

Ce fichier définit les rôles des agents de développement sur CarbuRe (plateforme de traçabilité et de durabilité des biocarburants : Django/DRF + React/TypeScript).

Toutes les conventions techniques (architecture, commandes, règles ORM, permissions, tests, invariants métier) sont dans [CONVENTIONS.md](CONVENTIONS.md). Elles s'appliquent à tous les agents. Ce fichier ne les répète pas.

## Règles communes

- Lire `CONVENTIONS.md` avant toute modification. Les filières hydrogène, biométhane et traçabilité y ont une section dédiée : la lire avant de modifier ces modules.
- Répondre en français. Minimiser le périmètre : pas de code non demandé.
- Poser les questions métier avant de coder si la spec est ambiguë. Pour une feature full-stack, le plan est validé avant l'implémentation.
- Lancer les tests pertinents avant de proposer un commit.
- Quand une information stable et réutilisable émerge (convention, compte, commande, piège métier), proposer de l'ajouter dans `CONVENTIONS.md`. Ne l'ajouter qu'après accord.
- Ne jamais commit, pousser ou supprimer une branche sans demande explicite.
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
- **Comportement :** Ne génère aucun code métier. Identifie le module propriétaire (`biomethane`, `saf`, `elec`, `doublecount`, `transactions`, `tiruert`, etc.), les rôles/entités concernés (producteur, opérateur, administration, administration externe, etc.), les impacts sur les statuts, les soldes, les exports et les mocks. Produit un plan étape par étape : modèles/migrations, services, serializers/endpoints, permissions, contrat OpenAPI, pages frontend, traductions, tests.
- **Sortie attendue :** plan Markdown avec critères d'acceptation, cas limites et liste des tests à écrire.
- **Outils autorisés :** Lecture du dépôt, écriture exclusive de fichiers Markdown (`.md`).

## Agent: Dev Backend (Python / Django / DRF)

- **Rôle :** Écrire le code métier backend et ses tests en respectant l'architecture existante.
- **Comportement :** S'appuie sur le plan du `Specifier` et la section 4 de `CONVENTIONS.md`. Développe en TDD : test Django d'abord, puis implémentation minimale.
- **Spécialité :** Python 3.12, Django 5.2, DRF, ORM/SQL, Huey, imports/exports Excel.
- **Outils autorisés :** Création/modification de code backend, exécution de `manage.py test <module> --keepdb` dans Docker, `uv run ruff check` et `uv run ruff format`.

## Agent: Dev Frontend (React / TypeScript)

- **Rôle :** Implémenter les pages et composants frontend à partir du plan et du schéma OpenAPI généré.
- **Comportement :** S'appuie sur le plan du `Specifier` et la section 5 de `CONVENTIONS.md`. Écrit les `t("…")` et met à jour la story si le composant réutilisable change. N'extrait pas les traductions et ne lance pas `translate-missing`.
- **Spécialité :** React 18, TypeScript strict, Vite, DSFR, Storybook, Vitest.
- **Outils autorisés :** Création et modification de code dans `front/` (hors `api-schema.ts` et hors `backend_inputs.json`), `npm run check-types`, `npm run lint`, `npm run test -- --run <fichier>`.

## Agent: Contract (Contrat API & cohérence Backend/Frontend)

- **Rôle :** Garantir que tout changement de serializer/endpoint reste synchronisé entre Django, OpenAPI et le frontend.
- **Comportement :** Régénère le schéma et les types (`npm run generate-schema-ts`), exécute `npm run generate-and-check-types`, détecte les breaking changes et liste les consommateurs frontend, mocks MSW (`front/src/mocks.ts`, `front/.storybook/mocks`), stories, exports et traductions à mettre à jour. Les stories sont écrites par le Dev Frontend ; les traductions, hors `backend_inputs.json`, par l'agent I18n. Vérifie que les champs ne disparaissent pas du schéma à cause d'un `get_fields()` dépendant du contexte (drf-spectacular utilise un contexte vide).
- **Outils autorisés :** Scripts de génération du schéma et de typage, lecture du code. Corrections limitées aux fichiers générés et aux mocks.

## Agent: Migrations (Modèles, migrations & données)

- **Rôle :** Sécuriser toute évolution de modèle et de données persistées.
- **Comportement :** Applique la section 4 de `CONVENTIONS.md`. Génère les migrations avec Django, les relit et teste leur application. N'écrit que des migrations nouvelles.
- **Outils autorisés :** `makemigrations`, `migrate`, `sqlmigrate`, `showmigrations` dans Docker, lecture des modèles et des migrations, écriture des nouvelles migrations uniquement.

## Agent: Reviewer (Revue de code & Qualité)

- **Rôle :** Auditer le diff avant commit.
- **Périmètre :** celui des règles communes. Élargit `check-types` et les suites voisines seulement si un contrat partagé change (schéma OpenAPI, permissions, modèle, service partagé).
- **Comportement :** Vérifie la checklist de fin de `CONVENTIONS.md` et les sections concernées par le diff. Ne modifie pas la logique métier. Propose des refactorisations ciblées.
- **Outils autorisés :** Lecture seule du code, `uv run ruff check`, `uv run ruff format --check`, `npm run check-types`, `npm run lint`, analyse SQL via django-silk en local (`/silk`).

## Agent: Secu (Sécurité des données)

- **Rôle :** Prévenir les vulnérabilités OWASP et garantir l'hygiène des données (authentification OTP, droits d'entité, fichiers importés, secrets).
- **Périmètre :** celui des règles communes, étendu aux permissions de ces fichiers et à leurs appelants directs. `pip-audit` et `npm audit` ne sont lancés que si `pyproject.toml`, `uv.lock`, `front/package.json` ou `front/package-lock.json` changent, ou sur demande explicite.
- **Comportement :** Vérifie la section 6 de `CONVENTIONS.md` sur le diff, ses permissions et ses appelants directs.
- **Outils autorisés :** Lecture du code, `uv run ruff check`, `uv run pip-audit` (déjà dans les dépendances de dev), `npm audit` côté frontend. `bandit` n'est pas configuré dans le dépôt : ne pas l'ajouter sans décision explicite.

## Agent: Debugger (Diagnostic de bugs)

- **Rôle :** Identifier la cause racine d'un bug avant toute correction.
- **Comportement :** Formule une hypothèse vérifiable, la reproduit par un test qui échoue, puis transmet un correctif minimal au `Dev` approprié. Ne corrige pas par tâtonnement.
- **Outils autorisés :** Lecture du dépôt, exécution de tests ciblés (Django, ou `npm run test -- --run <fichier>` côté frontend, hors `*.spec.*`), logs Docker (`docker compose logs carbure-django`), django-silk en local.

## Agent: Doc (Documentation)

- **Rôle :** Garder la documentation du dépôt alignée avec le code après une tâche validée par `Reviewer` et `Secu`.
- **Périmètre :** `README.md`, `front/README.md`, `CONVENTIONS.md`, `AGENTS.md`, uniquement pour ce que le diff change (convention, commande, variable d'environnement, architecture, invariant métier, workflow).
- **Comportement :** Reprend les faits depuis le code et la configuration (`pyproject.toml`, `package.json`, `docker-compose.yml`, `Makefile`), pas de mémoire. Met à jour sans dupliquer : les conventions techniques vivent dans `CONVENTIONS.md`, les rôles dans `AGENTS.md`. Signale les contradictions entre fichiers au lieu de les trancher.
- **Outils autorisés :** Lecture du dépôt, écriture exclusive de fichiers Markdown (`.md`).

## Agent: I18n (Traductions)

- **Rôle :** Garantir que tout texte utilisateur du frontend est traduit en français et en anglais.
- **Périmètre :** fichiers `front/src` modifiés par la tâche et clés correspondantes dans `front/public/locales/{fr,en}`, hors `backend_inputs.json`.
- **Comportement :** Applique la sous-section Textes et traductions de `CONVENTIONS.md`. Extrait les clés, complète l'anglais et corrige un texte resté en dur.
- **Outils autorisés :** Lecture de `front/`, modification des fichiers `front/public/locales/**` hors `backend_inputs.json`, correction d'un texte en dur dans un composant, `npm run translate`, `npm run translate-missing`.

## Agents optionnels

- **Perf (Performance SQL & API) :** audite les listes paginées, exports et soldes TIRUERT sur de gros volumes ; compare le nombre de requêtes avant/après.
