# Traceability

Noyau partagé des **actions** (lots). Une filière ne duplique pas ce module : elle branche un **handler**.

## Choix de conception

- **Facteurs figés sur l’action, pas sur la matière.** `lhv` (MJ/kg) et `density` (kg/l) sont copiés depuis le catalogue à la **création de la racine** (import Excel aujourd’hui, qui pose aussi `unit=kg`). Toute la chaîne de traçabilité convertit avec **ces** valeurs : un changement de PCI sur `Material` ne réécrit pas l’historique. À l’import Excel, une matière sans `lhv` **et** sans `density` lève une erreur interne (oubli catalogue, pas une erreur de cellule).
- **Le certificat fige le MJ à la valorisation.** `valorize()` écrit l’énergie du parent dans le `VALORIZE` (`unit=MJ`) et recopie `lhv` / `density` pour que toute la chaîne garde les mêmes facteurs. C’est le seul moment où une quantité convertie est **stockée**. Sans facteur sur la racine → `ConversionError`.
- **Le reste est calculé, pas persisté.** `mass` / `volume` / `energy` sont des annotations SQL (NULL si le facteur manque) :

```
mass   = volume × density
energy = mass × lhv
```

## Modèle

| Concept | Rôle |
|---|---|
| `Action` | POS, détenteur, matière, quantité + unité, snapshot `lhv` / `density`, site, logistique, GES |
| `ActionStatus` | Historique de workflow (`CREATED`, `PENDING`, …). Le statut courant est annoté sur le queryset |
| `Material` | Catalogue (`code`, `name`, `lhv`, `density`). Facteurs optionnels, ou strictement > 0 |

Import des matières  :

```bash
uv run python web/manage.py import_materials # dry-run
uv run python web/manage.py import_materials --dry-run=false
```

Fichier : [`fixtures/materials.csv`](fixtures/materials.csv). Un changement de PCI au catalogue **ne réécrit pas** les snapshots déjà posés sur les actions.

## Ce que la filière personnalise

Tout passe par `ActionIndustryHandler`, chargé via le query param `industry` (`handlers/registry.py`).

| Surcharge | Effet |
|---|---|
| `lookups` | Listes de choix `material` / `site` / `certificate` (API, Excel, validation) |
| `excel_columns` | Colonnes du template et mapping à l’import — voir [`docs/excel.md`](docs/excel.md) |
| `excel_import_serializer_class` | Validation d’import (surcharge filière) |
| `get_permissions` | Droits lecture / écriture |

Le registre `ACTION_HANDLERS` associe le code filière (`Action.INDUSTRIES`) à la classe handler, dans l’app de la filière (`web/<filiere>/handlers/`).

Côté front, les catalogues (`useActionFields`, `useActionColumns`, `useActionFilters`) sont **composés** par la page filière : ordre, libellés, options (types de site, etc.).

`quantity` affiche la quantité **stockée** (`quantity` + `unit`, saisissable). `mass` en est la vue convertie (kg, lecture seule, `null` si le facteur manque). Ce sont des factories privées de `hooks/action-fields` et `hooks/action-columns`. La page choisit lequel poser — lots H2 : `mass`. `volume` / `energy` suivront le même modèle.

---

## Tests

```bash
make test-backend module=traceability
```
