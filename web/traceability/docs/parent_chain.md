# Parcours de parents (`parent_chain`)

Code : `services/parent_chain.py`. Groupes de colonnes : `services/column_groups.py`.

Chaque action a un `parent`. La chaîne part de l'action et monte jusqu'à la racine, celle dont le parent est vide. La profondeur n'est pas connue à l'avance. Un `JOIN` ordinaire ne joint qu'un nombre fixe de niveaux. La requête récursive part des actions demandées, puis répète « prendre le parent » jusqu'à ce qu'il n'y en ait plus.

Le résultat n'est pas stocké. Les champs renvoyés : [`inherited_fields.md`](inherited_fields.md). La formule GES : [`total_emissions.md`](total_emissions.md).

## Un seul `WITH`, plusieurs groupes de colonnes

MySQL refuse d'emboîter deux requêtes récursives. Tout part dans un `WITH RECURSIVE` nommé `parent_chain`.

Un **groupe de colonnes** est trois fonctions, enregistrées dans `COLUMN_GROUPS` :

| Fonction | Rôle |
|---|---|
| `start` | Valeur sur l'action de départ |
| `climb` | Les mêmes clés, dans le même ordre, un cran plus haut. `cte.col.x` est la valeur déjà transportée. `F("colonne")` est la colonne du parent rejoint |
| `annotate` | Recopie la valeur finale sur l'action. Vide si la colonne ne sert qu'à filtrer |

Le `UNION ALL` aligne les colonnes par position. `start` et `climb` rendent les mêmes clés, dans le même ordre. Deux groupes ne portent pas le même nom de colonne. `_chain_cte` lève `ValueError` sinon.

`PAGE_COLUMN_GROUPS` charge ces deux groupes sur la liste et sur le détail :

- `emissions` — sommes GES
- `inherited_fields` — `previous_material_id` et `origin_material_id`. `attach_inherited_fields` charge ensuite les matières

Pour une action, la requête produit une ligne par cran. On garde celle dont le parent suivant est vide : les sommes sont complètes et les deux matières héritées sont résolues.

```
étape 0 (leaf)   origin=leaf  next_parent=middle  ei_sum=100
étape 1          origin=leaf  next_parent=root    ei_sum=110
étape 2          origin=leaf  next_parent=NULL    ei_sum=111
```

## Quand le parcours part

| Appel | Parcours |
|---|---|
| Liste | Filtres ordinaires, puis pagination. Le `COUNT` ne lance pas la CTE. `annotate_parent_chain` ne voit que les ids de la page, avec les deux groupes. MySQL interdit un `LIMIT` dans la sous-requête de la CTE. |
| Détail | `annotate_parent_chain` sur l'action demandée, avec les deux groupes. |
| `origin_material` | Avant la pagination, sur le queryset déjà filtré. `RecursiveFilterSet` ne part qu'une fois, après les filtres ordinaires, pour tous les filtres récursifs de l'URL. Il ne charge que les groupes nommés : ici `inherited_fields`, pas les GES. Les ids sont figés dans une liste Python, pour que le `COUNT` ne relance pas la CTE. La page refait ensuite le parcours complet, GES compris. |
| `GET /filters/?filter=origin_material` | `chain_column` sur le queryset déjà filtré par les autres paramètres. Une ligne par action, puis les libellés sont dédoublonnés. Tant que `origin_material` est dans l'URL, les options d'un autre filtre rejouent aussi cette remontée. |
| `/years/` | Pas de parcours. |

La liste et le détail appellent `Action.objects.annotate_actions`. Elle lance `annotate_parent_chain` sur les lignes demandées et charge les matières héritées. `quantity_available` vient de l'annotation du manager. `annotate_total_emissions` et `annotate_inherited_fields` ne demandent qu'un groupe. Ce ne sont pas le chemin de la liste.

Ne pas poser cette annotation sur `Action.objects`. La CTE lit `Action.unannotated`. Un manager déjà annoté s'imbriquerait dans la récursion.

## Pièges MySQL

| Dans le code | Pourquoi |
|---|---|
| `Action.unannotated.all().order_by()` | `ORDER BY`, `DISTINCT` et les sous-requêtes de statut sont interdits dans la CTE. Le manager filtre `quantity_available` avec une sous-requête de statut. Les ids du queryset appelant sont donc lus en liste Python avant le parcours. |
| `ei_sum` | Au `JOIN`, `ei` serait à la fois la somme transportée et la colonne de l'action. |
| `next_parent_id` | Même collision avec `parent_id`. |
| `_next_parent_id` | Une fois la CTE jointe à `Action`, le champ du modèle reprend le nom. On filtre la copie. |
| `Cast(Value(None), BigIntegerField())` | Un `NULL` nu fait deviner à MySQL une colonne trop étroite. L'id du parent ne rentre plus. |
| Ids en liste Python | Une sous-requête relancerait la CTE pour le `COUNT`, puis pour la page. |
| Liste d'ids vide | Pas de CTE. Django retire le membre vide d'un `UNION`, et MySQL refuse une CTE récursive qui n'a plus de `UNION`. |

## Valeur stockée sur la racine

`ROOT_COLUMNS` est vide. Aucun filtre ne lit une valeur écrite sur la ligne racine. Le parcours ne porte pour l'instant que `previous_material_id` et `origin_material_id`. `origin_material` n'y entre pas : la première matière non vide peut être sous la racine.

Le jour où une clé y entre, `filter_by_chain` trouve les racines avec un `WHERE` ordinaire :

- elles sont moins nombreuses que la liste déjà filtrée (un `pos_id`, une seule chaîne) : on descend vers les enfants ;
- elles sont aussi nombreuses ou plus (un producteur qui possède presque toutes les racines) : on remonte depuis la liste. Descendre matérialiserait un `IN` énorme.

Les autres colonnes du même filtre continuent d'être filtrées par la remontée.

Mesure locale unique, client Django, deuxième appel, Silk actif, environ 11 000 valorisations sur 100 000 actions. Un seul `pos_id` descend en moins de 1 ms de CTE, contre environ 220 ms en remontant ces valorisations. À nombre de chaînes égal, la descente ne coûte pas moins cher.

Les tests `test_root_columns_descend_when_the_roots_are_fewer_than_the_list` et `test_root_columns_climb_when_the_list_is_no_larger_than_the_roots` patchent le dictionnaire. Ils vérifient le choix de plan. Ils ne mesurent pas le temps. Le choix compare le nombre de racines au nombre d'actions, pas le nombre de descendants.

## Ajouter une colonne renvoyée

Pas de nouveau groupe. `PAGE_COLUMN_GROUPS` charge déjà `inherited_fields`.

1. `inherited_start()` — valeur au départ. Pour ignorer celle de l'action, `_empty_id()`. Pour partir de la sienne, `F("ma_colonne")`.
2. `inherited_climb()` — la même clé, au même rang. Garder la première valeur trouvée : `Coalesce(cte.col.ma_colonne, F("ma_colonne"), output_field=_ID)`. La remplacer par celle du parent à chaque cran : `F("ma_colonne")`.
3. `inherited_annotation()` — recopier `cte.col.ma_colonne`.
4. `attach_inherited_fields()` — charger la ligne et poser la clé JSON.
5. `ActionInheritedFieldsSerializer`.
6. Régénérer le schéma (`make generate-and-check-types`) et afficher la clé côté front.
7. Un test sur une feuille : une seule CTE, et la valeur attendue.

## Ajouter un filtre

Modèle : `OriginMaterialFilter`. C'est aujourd'hui le seul filtre de ce parcours. Le paramètre est un code matière.

1. Sous-classer `RecursiveColumnFilter`. Poser `column` (une clé de `start()`) et `group`. À l'import, la classe vérifie que le groupe existe et que `start()` produit cette colonne.
2. `to_values` traduit le paramètre d'URL vers la valeur stockée. `to_labels` fait l'inverse pour `GET /filters/`. Sans ces deux méthodes, l'URL et le menu parlent la valeur brute.
3. Déclarer le filtre sur `ActionFilter`, qui hérite de `RecursiveFilterSet`.
4. Côté front : la clé dans `ActionFilter`, une entrée dans `useActionFilters`, et `use-combined-query.tsx` si la page l'envoie avec les autres filtres.

`RecursiveFilterSet` laisse passer les filtres ordinaires, puis rassemble les filtres récursifs présents dans l'URL et ne lance qu'une remontée. Un paramètre dont aucune ligne stockée ne correspond renvoie un queryset vide.

## Ajouter un groupe de colonnes

Utile pour une question du type « un ancêtre a le type INIT », qui n'est pas un champ déjà porté par `inherited_fields`.

1. `start`, `climb`, et `annotate` si la liste doit renvoyer la valeur. Pour un prédicat : au départ, la valeur de l'action. En montant, garder `cte.col` dès qu'il est vrai, sinon lire le parent. Une fois vrai, la valeur le reste jusqu'à la racine.
2. L'enregistrer dans `COLUMN_GROUPS`.
3. L'ajouter à `PAGE_COLUMN_GROUPS` seulement s'il part sur chaque page. Sinon laisser `annotate` vide : le filtre ne charge que les groupes qu'il nomme.
4. Le filtre est une sous-classe de `RecursiveColumnFilter` avec ce nom de groupe.

La clé ne doit pas déjà exister sur un autre groupe.

## Activer le raccourci racine

Seulement si la valeur est écrite sur l'action racine (`holder_id`, `pos_id`) et qu'un filtre la lit.

```python
ROOT_COLUMNS = {
    "root_pos_id": "pos_id",
}
```

La clé est une colonne déjà portée par la remontée. La valeur est le champ sur l'action racine.
