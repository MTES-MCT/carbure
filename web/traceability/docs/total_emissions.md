# Cumul GES (`total_emissions`)

Code : `services/total_emissions.py`. Tests : `tests/services/test_total_emissions.py`.

On annote chaque action listée avec les GES **de sa chaîne de parents** (elle-même → parent → … → racine).

```
total = eec + el + ei + ep + etd + eu - eccs - esca - eccr
```

Les postes `eec`, `el`, `ei`, `ep`, `etd`, `eu`, `eccs`, `esca` et `eccr` du JSON sont les **sommes** sur ce chemin, `total` est la formule ci-dessus.

---

## Exemple

Trois actions, `leaf → middle → root` :

| action | ei | ep | etd | eu | eccs | parent |
|--------|----|----|-----|----|------|--------|
| root   | 1  | 2  | 3   | 4  | 5    | —      |
| middle | 10 | 20 | 30  | 40 | 50   | root   |
| leaf   | 100| 200| 300 | 400| 500  | middle |

`total_emissions` de **leaf** = sommes du chemin leaf+middle+root :

```
ei=111, ep=222, etd=333, eu=444, eccs=555
total = 111+222+333+444-555 = 555
```

root ne cumule qu’elle-même (`total=5`) ; middle = root+middle (`total=55`).

---

## Une requête, deux morceaux

django-cte sépare ce que MySQL écrit en **un** `WITH RECURSIVE … SELECT`.

### 1. `_parent_path_cte` — remonter et additionner

Pour chaque action demandée (`origin_id`), une ligne par **étape** (un cran vers le parent) :

```
étape 0 (leaf)   origin=leaf  next_parent=middle  ei_sum=100
étape 1          origin=leaf  next_parent=root    ei_sum=100+10=110
étape 2          origin=leaf  next_parent=NULL    ei_sum=110+1=111   ← racine, on s’arrête
```

La récursion : `JOIN action ON action.id = cte.next_parent_id`, puis `ei_sum + action.ei`. Pareil pour ep/etd/eu/eccs.

SQL équivalent (simplifié, un seul poste) :

```sql
WITH RECURSIVE cte AS (
  -- départ : les actions de la page
  SELECT id AS origin_id, parent_id AS next_parent_id, ei AS ei_sum
  FROM action
  WHERE id IN (/* ids listés */)

  UNION ALL

  -- un cran vers le parent, on ajoute ses GES
  SELECT cte.origin_id, parent.parent_id, cte.ei_sum + parent.ei
  FROM cte
  JOIN action AS parent ON parent.id = cte.next_parent_id
)
SELECT * FROM cte;
```

### 2. `annotate_total_emissions` — garder la dernière étape

La CTE a **toutes** les étapes. On ne veut que celle arrivée à la racine (`next_parent_id IS NULL`) : les sommes sont alors complètes. On la `JOIN` sur l’action d’origine pour conserver `select_related` / statut, et on construit le JSON.

---

## Pièges MySQL (pourquoi le Python a l’air tordu)

| Dans le code | Pourquoi |
|--------------|----------|
| `Action.unannotated.all().order_by()` | Interdit `ORDER BY` / `DISTINCT` / sous-requêtes de statut **dans** une CTE récursive. `Meta.ordering` et le manager annoté cassent la requête. |
| `ei_sum` et pas `ei` | Collision avec la colonne `action.ei` au `JOIN`. |
| `next_parent_id` | Pareil avec `action.parent_id`. |
| `_next_parent_id` + `filter(…isnull=True)` | On ne peut pas filtrer directement `cte.next_parent_id` une fois joint à `Action` (le champ modèle gagne). |

---

## Où c’est branché

`ActionViewset` : **retrieve** annote après le filtre `pk` ; **list** pagine d’abord, puis annote les ids de la page (MySQL interdit `LIMIT` dans la sous-requête de la CTE). Le `COUNT` de pagination s’exécute donc sur le queryset **sans** CTE.

Ne pas remettre `annotate_total_emissions` sur `Action.objects` (manager) : ça recalculerait le cumul pour toute la table, y compris `/years/` et `/filters/`.
