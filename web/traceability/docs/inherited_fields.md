# Champs hérités (`inherited_fields`)

Colonnes : `services/inherited_fields.py`. Parcours : `services/parent_chain.py`. Tests : `tests/services/test_inherited_fields.py`.

On annote chaque action listée en remontant sa chaîne de parents, jusqu'à la racine, le même parcours que les GES. Deux matières en sortent. Chacune a la même forme que `material` sur l'action (`id`, `code`, `name`, `lhv`, `density`, `unit`).

```json
"inherited_fields": {
  "previous_material": { "id": 2, "code": "CH4", "name": "Méthane", "lhv": "50.000000", "density": null, "unit": "kg" },
  "origin_material": { "id": 1, "code": "H2", "name": "Hydrogène", "lhv": "120.000000", "density": "0.800000", "unit": "kg" }
}
```

`previous_material` est la matière non vide la plus proche **au-dessus** de l'action. La sienne est ignorée. Rien au-dessus : `null`.

`origin_material` est la première matière non vide en partant de la racine. Si l'action est la seule à en déclarer une, c'est la sienne.

`material` sur l'action elle-même ne change pas : c'est la valeur stockée. L'unité affichée à côté de `quantity` est celle de cette matière, ou celle de `previous_material` quand l'action n'en stocke pas.

Si aucune action de la chaîne ne porte de matière, les deux valent `null`. L'action reste dans la liste.

---

## Exemple

| action | matière stockée | parent |
|--------|-----------------|--------|
| root   | H2              | —      |
| middle | —               | root   |
| leaf   | BIO             | middle |

| action | previous_material | origin_material |
|--------|-------------------|-----------------|
| root   | —                 | H2              |
| middle | H2                | H2              |
| leaf   | H2                | H2              |

Si **middle** déclare DIESEL, **leaf** a `previous_material` DIESEL et `origin_material` H2.

---

## Le même parcours que les GES

`annotate_parent_chain` construit **une** CTE récursive. `inherited_fields.py` y ajoute les deux colonnes :

```sql
WITH RECURSIVE parent_chain AS (
  SELECT id AS origin_id,
         parent_id AS next_parent_id,
         NULL AS previous_material_id,
         material_id AS origin_material_id
  FROM action
  WHERE id IN (/* ids listés */)

  UNION ALL

  SELECT parent_chain.origin_id,
         parent.parent_id,
         COALESCE(parent_chain.previous_material_id, parent.material_id),
         COALESCE(parent.material_id, parent_chain.origin_material_id)
  FROM parent_chain
  JOIN action AS parent ON parent.id = parent_chain.next_parent_id
)
```

`previous_material_id` garde la première valeur trouvée en remontant. `origin_material_id` se laisse écraser par le parent, donc la valeur la plus proche de la racine gagne.

On ne garde que la ligne arrivée à la racine (`next_parent_id IS NULL`).

La vue appelle ensuite `attach_inherited_fields` sur les actions déjà chargées (la page, ou l'action du détail). Un `in_bulk` charge les matières, puis pose `inherited_fields` sur chaque instance. `MaterialSerializer` sérialise l'instance. Si l'id est vide, la matière vaut `null`.

Un champ de plus se déclare aux mêmes endroits : `inherited_start`, `inherited_climb`, `inherited_annotation`, `attach_inherited_fields`, et `ActionInheritedFieldsSerializer`.

`annotate_inherited_fields` est la façade qui demande uniquement ces colonnes. La vue appelle `annotate_parent_chain` avec les deux résultats, puis `attach_inherited_fields`.

---

## Où c'est branché

`ActionViewset` appelle `annotate_parent_chain` : **retrieve** sur l'action demandée, **list** après pagination, sur les ids de la page. Pas de `LIMIT` dans la sous-requête de la CTE. `attach_inherited_fields` suit, sur cette même action ou cette même page.

`/years/` et `/filters/` n'appellent pas cette annotation.

Le filtre `material` continue de porter sur la matière **stockée**. Brancher un filtre sur `inherited_fields` demanderait d'exécuter la CTE avant la pagination.
