# Champs hérités (`inherited_fields`)

Colonnes : `services/inherited_fields.py`. Parcours : `services/parent_chain.py`. Tests : `tests/services/test_inherited_fields.py`.

On annote chaque action listée avec la **première valeur non vide** rencontrée en remontant sa chaîne (elle-même, puis son parent, et ainsi de suite). Le parcours va jusqu'à la racine, le même que les GES : un `COALESCE` conserve la première valeur trouvée, un ancêtre plus lointain ne l'écrase pas.

Aujourd'hui le seul champ résolu est `material`. Il a la même forme que `material` sur l'action (`id`, `code`, `name`, `lhv`, `density`, `unit`).

```json
"inherited_fields": {
  "material": { "id": 1, "code": "H2", "name": "Hydrogène", "lhv": "120.000000", "density": "0.800000", "unit": "kg" }
}
```

Si aucune action de la chaîne ne porte de matière, `material` vaut `null`. L'action reste dans la liste.

`material` sur l'action elle-même ne change pas : c'est la valeur stockée. `inherited_fields.material` est la matière à afficher. Son `unit` est l'unité affichée à côté de `quantity`. Un `VALORIZE` ne stocke pas de matière : l'unité du certificat est donc celle du parent.

---

## Exemple

| action | matière stockée | parent |
|--------|-----------------|--------|
| root   | H2              | —      |
| middle | —               | root   |
| leaf   | —               | middle |

`inherited_fields.material` de **leaf** et de **middle** est H2. Celui de **root** est H2 aussi : la recherche commence par l'action elle-même.

Si **middle** redéclare une matière, **leaf** reçoit celle de middle, pas celle de root.

---

## Le même parcours que les GES

`annotate_parent_chain` construit **une** CTE récursive. `inherited_fields.py` y ajoute la colonne matière :

```sql
WITH RECURSIVE parent_chain AS (
  SELECT id AS origin_id, parent_id AS next_parent_id, material_id AS found_material_id
  FROM action
  WHERE id IN (/* ids listés */)

  UNION ALL

  SELECT parent_chain.origin_id,
         parent.parent_id,
         COALESCE(parent_chain.found_material_id, parent.material_id)
  FROM parent_chain
  JOIN action AS parent ON parent.id = parent_chain.next_parent_id
)
```

On ne garde que la ligne arrivée à la racine (`next_parent_id IS NULL`). La CTE s'arrête à `found_material_id`.

La vue appelle ensuite `attach_inherited_fields` sur les actions déjà chargées (la page, ou l'action du détail). Un `in_bulk` charge les matières, puis pose `inherited_fields` sur chaque instance. `MaterialSerializer` sérialise l'instance. Si l'id est vide, `material` vaut `null`.

Un champ de plus se déclare aux mêmes endroits : `inherited_start`, `inherited_climb`, `inherited_annotation`, `attach_inherited_fields`, et `ActionInheritedFieldsSerializer`.

`annotate_inherited_fields` est la façade qui demande uniquement ces colonnes. La vue appelle `annotate_parent_chain` avec les deux résultats, puis `attach_inherited_fields`.

---

## Où c'est branché

`ActionViewset` appelle `annotate_parent_chain` : **retrieve** sur l'action demandée, **list** après pagination, sur les ids de la page. Pas de `LIMIT` dans la sous-requête de la CTE. `attach_inherited_fields` suit, sur cette même action ou cette même page.

`/years/` et `/filters/` n'appellent pas cette annotation.

Le filtre `material` continue de porter sur la matière **stockée**. Brancher un filtre sur `inherited_fields` demanderait d'exécuter la CTE avant la pagination.
