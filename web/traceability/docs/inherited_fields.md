# Champs hérités (`inherited_fields`)

Calculés à la lecture par le parcours de parents. Le mécanisme, les filtres et `ROOT_COLUMNS` : [`parent_chain.md`](parent_chain.md).

| Champ | Règle |
|---|---|
| `previous_material` | Première matière non vide au-dessus. La matière de l'action est ignorée. `null` si rien au-dessus. |
| `origin_material` | Première matière non vide depuis la racine. La sienne si rien au-dessus. |
| `nearest_site` | Premier site au-dessus. Le sien est ignoré. `null` sur une racine. |
| `producer` | Détenteur de la racine. |
| `root_pos` | `pos_id` de la racine. |

`material` stocké ne change pas. L'unité de `quantity`, ainsi que la masse, le volume et l'énergie, utilisent la matière stockée, sinon `previous_material`.
