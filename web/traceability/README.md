# Traceability

Noyau partagé des **actions** (lots). Une filière ne duplique pas ce module : elle branche un **handler**.

## Choix de conception

- **Les facteurs vivent sur la matière.** `lhv` (MJ/kg) et `density` (kg/l) sont lus sur `Material` à chaque calcul. Un changement de PCI au catalogue s’applique aux actions déjà créées. À l’import Excel, une matière sans `lhv` **et** sans `density` lève une erreur interne (oubli catalogue, pas une erreur de cellule).
- **La valorisation recopie la quantité.** `valorize()` crée un enfant `VALORIZE` avec la `quantity` du parent et sans matière. Rien n’est converti ni figé en MJ.
- **Le reste est calculé, pas persisté.** `mass` / `volume` / `energy` sont des annotations SQL à partir de la matière **stockée** (`material.lhv` / `material.density`, NULL si la matière ou le facteur manque) :

```
mass   = volume × density
energy = mass × lhv
```

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

`inherited_fields` et `total_emissions` sont calculés à la lecture (liste paginée et détail) par le même parcours de parents (`services/parent_chain.py`). Aujourd'hui, le seul champ hérité est `material`. Voir [`docs/inherited_fields.md`](docs/inherited_fields.md).

## Ce que la filière personnalise

Tout passe par `ActionIndustryHandler`, chargé via le query param `industry` (`handlers/registry.py`).

| Surcharge | Effet |
|---|---|
| `lookups` | Listes de choix `material` / `site` / `certificate` (API, Excel, validation) |
| `excel_columns` | Colonnes du template et mapping à l’import — voir [`docs/excel.md`](docs/excel.md) |
| `excel_import_serializer_class` | Validation d’import (surcharge filière) |
| `read_permission`, `write_permission`, `admin_permission` | Droits pour chaque endpoint |
| `scope_queryset` | Filtre sur `industry`, puis détenteur ou parent. Si on est admin, on affiche toutes les données de la filière |

Le registre `ACTION_HANDLERS` associe le code filière (`Action.INDUSTRIES`) à la classe handler, dans l’app de la filière (`web/<filiere>/handlers/`).

Côté front, les catalogues (`useActionFields`, `useActionColumns`, `useActionFilters`) sont **composés** par la page filière : ordre, libellés, options (types de site, etc.). Une page peut passer `emptyState` à `ActionsPage` : il remplace la liste quand elle est chargée, sans filtre, et sans résultat.

`quantity` affiche la quantité **stockée** avec l’unité de la matière héritée (`inherited_fields.material.unit`). Un `VALORIZE` n’a pas de matière stockée : l’unité vient donc du parent. `mass` en est la vue convertie depuis la matière stockée (kg, lecture seule, `null` si elle ou le facteur manque). Ce sont des factories privées de `hooks/action-fields` et `hooks/action-columns`. La page choisit lequel poser — lots H2 : `mass`, certificats H2 : `quantity`. `volume` / `energy` suivent le même modèle.

---

## Tests

```bash
make test-backend module=traceability
```
