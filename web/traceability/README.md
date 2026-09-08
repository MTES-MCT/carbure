# Traceability

Noyau partagé des **actions** (lots). Une filière ne duplique pas ce module : elle branche un **handler**.

## Modèle

| Concept | Rôle |
|---|---|
| `Action` | Unité de traçabilité : POS, détenteur, matière, quantité (MJ), site, logistique, GES (`ei`/`ep`/`etd`/`eu`/`eccs`) |
| `ActionStatus` | Historique de workflow (`CREATED`, `PENDING`, …). Le statut courant est annoté sur le queryset |
| `Material` | Catalogue matières (`code`, `name`) |

## Ce que la filière personnalise

Tout passe par `ActionIndustryHandler`, chargé via le query param `industry` (`handlers/registry.py`).

| Surcharge | Effet |
|---|---|
| `lookups` | Listes de choix `material` / `site` / `certificate` (API, Excel, validation) |
| `excel_columns` | Colonnes du template et mapping à l’import — voir [`docs/excel.md`](docs/excel.md) |
| `excel_import_serializer_class` | Validation d’import (surcharge filière) |
| `get_permissions` | Droits lecture / écriture |

Le registre `ACTION_HANDLERS` associe le code filière (`Action.INDUSTRIES`) à la classe handler, dans l’app de la filière (`web/<filiere>/handlers/`).

Côté front, les hooks génériques (`useActionFields`, `useActionColumns`, `useActionFilters`) sont **composés** par la page filière : ordre, libellés, options (types de site, etc.).

---

## Tests

```bash
make test-backend module=traceability
```
