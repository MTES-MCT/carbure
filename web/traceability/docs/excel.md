# Import Excel des actions

Comment une filière **étend** le template et l’import, sans recopier le noyau.

Flux : `excel_columns` (template) → parse (`header` → `key`) → serializer du handler → `create`.  
Les clés qui ne sont pas des champs du modèle `Action` sont **écartées** au `create` générique.

---

## Registre et helper

Les colonnes du noyau vivent dans `ACTION_EXCEL_COLUMNS` (`handlers/excel.py`) : header, commentaire, options (listes déroulantes), couleur.

```python
from traceability.handlers.excel import excel_column, EXCEL_PRODUCTION_COLOR

excel_column("pos_id")
excel_column("material", header="Nature de la matière")  # override
```

Couleurs de section, à réutiliser plutôt que de les redéfinir :

- `EXCEL_PRODUCTION_COLOR`
- `EXCEL_TRANSPORT_COLOR`
- `EXCEL_CONSUMPTION_COLOR`

Le mixin d’import instancie `request.handler.excel_import_serializer_class`.

Erreurs **fichier** (pas une ligne) : `{ "error": "<CODE>" }` — `EMPTY_FILE`, `INVALID_FILE`. Le front traduit le code. Les erreurs de cellules restent dans `validation_errors`. Une colonne peut être déclarée unique dans le fichier : chaque doublon est une erreur de cellule.

**Sans `key`**, la colonne apparaît dans le fichier et **disparaît au parse** : aucune validation, aucune persistence. Toujours poser un `key` dès que la colonne doit être lue.

---

## 1. Champ du noyau (`Action`)

La colonne existe déjà dans le registre. La filière l’inclut (éventuellement en changeant le libellé) ; le serializer générique s’en charge.

```python
class ExampleIndustryHandler(ActionIndustryHandler):
    excel_columns = [
        excel_column("pos_id"),
        excel_column("material", header="Nature de la matière"),
        excel_column("quantity", header="Quantité consommée (MJ)"),
        excel_column("site", comment="Liste de choix — nom du site dans Carbure"),
    ]
```

Pour **ajouter** un champ au noyau (toutes filières) : colonne sur `Action` + entrée dans `ACTION_EXCEL_COLUMNS` + champ sur `ActionExcelImportSerializer` + hook front.

---

## 2. Cas temporaire : valider sans stocker

> **Temporaire.** Une colonne Excel à contrôler à l’import sans la persister. Ce n’est pas un pattern à généraliser : dès que la donnée a une vie après l’import, elle va sur `Action` (cas 1) ou une table d’extension filière.  
> Aujourd’hui : `write_only` sur le serializer filière + `excelImport.fieldLabels` au front.

Même `key` + champ serializer ; le `create` générique ignore les clés hors modèle `Action`.

```python
class ExampleIndustryHandler(ActionIndustryHandler):
    excel_import_serializer_class = ExampleIndustryExcelImportSerializer
    excel_columns = [
        {
            "key": "external_ref",
            "header": "Référence interne",
            "comment": "Identifiant dans votre système",
            "color": EXCEL_PRODUCTION_COLOR,
        },
        excel_column("pos_id"),
    ]
```

```python
class ExampleIndustryExcelImportSerializer(ActionExcelImportSerializer):
    external_ref = serializers.CharField(write_only=True)

    class Meta(ActionExcelImportSerializer.Meta):
        fields = [*ActionExcelImportSerializer.Meta.fields, "external_ref"]
```

`required=True` par défaut sur `CharField` : cellule vide → erreur de ligne, même pipeline que le noyau.

Côté front, les erreurs utilisent le `key` (`external_ref`). Pour afficher le libellé Excel :

```ts
excelImport={{
  fieldLabels: { external_ref: t("Référence interne") },
}}
```

