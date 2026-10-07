# Traceability

Noyau partagé des **actions** (lots). Une filière ne duplique pas ce module : elle branche un **handler**.

## Choix de conception

- **Les facteurs vivent sur la matière.** `lhv` (MJ/kg) et `density` (kg/l) sont lus sur `Material` à chaque calcul. Un changement de PCI au catalogue s’applique aux actions déjà créées. À l’import Excel, une matière sans `lhv` **et** sans `density` lève une erreur interne (oubli catalogue, pas une erreur de cellule).
- **Le certificat fige le MJ à la valorisation.** `valorize()` écrit l’énergie du parent dans le `VALORIZE` et lui affecte la matière `VALORIZED_ENERGY` (code `VALORIZED-ENERGY`, unité MJ). C’est le seul moment où une quantité convertie est **stockée**. Cette matière n’a pas de PCI ni de masse volumique : la quantité du certificat s’affiche en MJ, mass/volume restent vides. Sans `lhv` sur la matière du parent → `ConversionError`.
- **Le reste est calculé, pas persisté.** `mass` / `volume` / `energy` sont des annotations SQL à partir de `material.lhv` / `material.density` (NULL si le facteur manque) :

```
mass   = volume × density
energy = mass × lhv
```

## Modèle

| Concept | Rôle |
|---|---|
| `Action` | POS, détenteur, matière, quantité, site, logistique, GES |
| `ActionStatus` | Historique de workflow (`CREATED`, `PENDING`, …). Le statut courant est annoté sur le queryset |
| `Material` | Catalogue (`code`, `name`, `unit`, `lhv`, `density`). L’unité native de `quantity` vit ici. Facteurs optionnels, ou strictement > 0 |

Import des matières :

```bash
uv run python web/traceability/fixtures/load_materials.py
```

Fichier : [`fixtures/materials.csv`](fixtures/materials.csv), le catalogue éditable. Le script crée ensuite la matière système `VALORIZED_ENERGY` (code `VALORIZED-ENERGY`, unité MJ, sans PCI ni densité). Une migration rattache les actions `VALORIZE` déjà en base à cette matière. Un changement de PCI au catalogue s’applique aux actions liées à cette matière. Chargé automatiquement au deploy (`bin/post_deploy.sh`).

Le `DELETE` supprime l'action de la bdd. Il n'est autorisé que pour une action `INIT` dont le statut courant est `PENDING` ou `REJECTED`.
| `Material` | Catalogue matières (`code`, `name`) |

Le catalogue est chargé au déploiement (`bin/post_deploy.sh`) depuis [`fixtures/materials.csv`](fixtures/materials.csv) :

```bash
uv run python web/traceability/fixtures/load_materials.py
```

## Ce que la filière personnalise

Tout passe par `ActionIndustryHandler`, chargé via le query param `industry` (`handlers/registry.py`).

| Surcharge | Effet |
|---|---|
| `lookups` | Listes de choix `material` / `site` / `certificate` (API, Excel, validation) |
| `excel_columns` | Colonnes du template et mapping à l’import — voir [`docs/excel.md`](docs/excel.md) |
| `excel_import_serializer_class` | Validation d’import (surcharge filière) |
| `get_permissions` | Droits lecture / écriture |

Le registre `ACTION_HANDLERS` associe le code filière (`Action.INDUSTRIES`) à la classe handler, dans l’app de la filière (`web/<filiere>/handlers/`).

Côté front, les hooks génériques (`useActionFields`, `useActionColumns`, `useActionFilters`) sont **composés** par la page filière : ordre, libellés, options (types de site, etc.). Une page peut passer `emptyState` à `ActionsPage` : il remplace la liste quand elle est chargée, sans filtre, et sans résultat.

`quantity` affiche la quantité **stockée** (`quantity` + unité de la matière, saisissable). `mass` en est la vue convertie (kg, lecture seule, `null` si le facteur manque). Ce sont des factories privées de `hooks/action-fields` et `hooks/action-columns`. La page choisit lequel poser — lots H2 : `mass`. `volume` / `energy` suivront le même modèle.

---

## Tests

```bash
make test-backend module=traceability
```
