# Traceability

Noyau partagé des **actions** (lots) toutes filières.

## Modèle

| Concept | Rôle |
|---|---|
| `Action` | Unité de traçabilité : POS, détenteur, matière, quantité (MJ), site, logistique, GES (`ei`/`ep`/`etd`/`eu`/`eccs`) |
| `ActionStatus` | Historique de workflow (`CREATED`, `PENDING`, …). Le statut courant est annoté sur le queryset |
| `Material` | Catalogue matières (`code`, `name`) |


## Plugin filière (`ActionIndustryHandler`)

Chargé depuis le query param `industry` (`get_action_handler` dans `handlers/registry.py`).

Le handler surcharge :

- `lookups` — querysets `material` / `site` / `certificate` (H2 : codes `H2-*`, stations HRS de l’entité, CertifHy)
- `excel_columns` — template + parse Excel
- `excel_import_serializer_class` — validation d’import
- `get_permissions`

Nouvelle filière : classe dans l’app (`h2/handlers/…`), entrée dans `ACTION_HANDLERS`, choix sur `Action.INDUSTRIES`.

## Excel

Colonnes génériques : `ACTION_EXCEL_COLUMNS` + `excel_column(key, **overrides)` (`handlers/excel.py`). Couleurs de section partagées (`EXCEL_PRODUCTION_COLOR`, `TRANSPORT`, `CONSUMPTION`).

Trois natures de colonnes :

1. **Noyau persisté** — `excel_column("pos_id")` + serializer générique + champ `Action`
2. **Filière persistée** — serializer filière + colonne `Action` ou table d’extension
3. **Filière transitoire** — `key` sur la spec Excel + champ `write_only` sur le serializer filière. Validé, puis écarté au `create` (les clés hors modèle `Action` sont ignorées)

Aujourd’hui en transitoire H2 : `lot_id` (`Id du lot`, obligatoire). Les autres colonnes H2 sans `key` (batch, masse, type de carburant, consommation sur site) sont affichées dans le template mais **ignorées au parse**.

Le mixin d’import instancie `request.handler.excel_import_serializer_class`.

## Front

Hooks génériques (`useActionFields`, `useActionColumns`, `useActionFilters`) composés par la page filière (`front/src/h2/pages/lots/`). Labels d’erreur Excel transitoires : `excelImport.fieldLabels` (ex. `lot_id` → « Id du lot »).

## Tests

```bash
make test-backend module=traceability
make test-backend module=h2.tests.handlers
```
