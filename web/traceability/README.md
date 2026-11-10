# Traceability

Noyau partagé des **actions** (lots). Une filière ne duplique pas ce module : elle branche un **handler**.

| Doc | Sujet |
|---|---|
| [`docs/parent_chain.md`](docs/parent_chain.md) | Parcours récursif, filtres, ajout d'une colonne |
| [`docs/inherited_fields.md`](docs/inherited_fields.md) | Règles des champs hérités |
| [`docs/total_emissions.md`](docs/total_emissions.md) | Formule du cumul GES |
| [`docs/excel.md`](docs/excel.md) | Colonnes et import Excel |

## Choix de conception

- **La valorisation recopie la quantité.** `valorize()` crée un enfant `VALORIZE` avec la `quantity` du parent et sans matière. Rien n’est converti ni figé en MJ.
- **`quantity` et `quantity_available` sont renvoyés tels quels.** `quantity` est la valeur stockée. `quantity_available` vaut `quantity` moins la somme des `quantity` des enfants directs, hors `DELETED` et `REJECTED`. Un enfant sans statut compte. Même unité que `quantity`. Pas de conversion en masse, volume ou énergie.

## Modèle

| Concept | Rôle |
|---|---|
| `Action` | POS, détenteur, matière, quantité, site, logistique, GES. Fichier source optionnel (`file` → `core.StoredFile`, renseigné à l’import Excel, non exposé à l’API) |
| `ActionStatus` | Historique de workflow (`CREATED`, `PENDING`, …). Le statut courant est annoté sur le queryset |
| `Material` | Catalogue (`code`, `name`, `unit`, `lhv`, `density`). L’unité native de `quantity` vit ici. Facteurs optionnels, ou strictement > 0 |

Import des matières :

```bash
uv run python web/traceability/fixtures/load_materials.py
```

Fichier : [`fixtures/materials.csv`](fixtures/materials.csv), le catalogue éditable. Chargé automatiquement au deploy (`bin/post_deploy.sh`).

Le `DELETE` supprime l'action de la bdd. Il n'est autorisé que pour une action `INIT` dont le statut courant est `PENDING` ou `REJECTED`.

`inherited_fields` et `total_emissions` sont calculés à la lecture par le même parcours de parents ([`docs/parent_chain.md`](docs/parent_chain.md)).

## Ce que la filière personnalise

Tout passe par `ActionIndustryHandler`, chargé via le query param `industry` (`handlers/registry.py`).

| Surcharge | Effet |
|---|---|
| `lookups` | Listes de choix `material` / `site` / `certificate` (API, Excel, validation) |
| `excel_columns` | Colonnes du template et mapping à l’import — voir [`docs/excel.md`](docs/excel.md) |
| `excel_import_serializer_class` | Validation d’import (surcharge filière) |
| `read_permission`, `write_permission`, `admin_permission` | Droits pour chaque endpoint |
| `scope_queryset` | Filtre sur `industry`, puis détenteur ou parent. Si on est admin, on affiche toutes les données de la filière |
| `transitions`, `creations` | Matrices de la filière. Une ligne absente est un droit absent. `valorize` et `refuse` lisent `transitions` |

`can_change_status(handler, type, statut de départ, statut d’arrivée)` renvoie la `Transition`, ou `None`. `can_create(handler, type, parent=None)` renvoie la `Creation`, ou `None`. Chaque ligne porte le statut de naissance de l’action (`status`, sans valeur par défaut). Sans parent, seule une création `root` convient. Avec parent, son type et son statut courant doivent correspondre à `parent` et `parent_status` de la ligne. Une ligne nomme au plus un parent : plusieurs parents possibles s’écrivent en plusieurs lignes.

Le registre `ACTION_HANDLERS` associe le code filière (`Action.INDUSTRIES`) à la classe handler, dans l’app de la filière (`web/<filiere>/handlers/`).

Côté front, les catalogues (`useActionFields`, `useActionColumns`, `useActionFilters`) sont **composés** par la page filière : ordre, libellés, options (types de site, etc.). Une page peut passer `emptyState` à `ActionsPage` : il remplace la liste quand elle est chargée, sans filtre, et sans résultat.

`quantity` affiche la quantité **stockée** avec l’unité de la matière stockée, ou celle de `previous_material` quand l’action n’en a pas.

---

## Tests

```bash
make test-backend module=traceability
```
