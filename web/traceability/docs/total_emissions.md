# Cumul GES (`total_emissions`)

Sommes le long de la chaîne de parents : l'action, puis ses parents, jusqu'à la racine. Le parcours : [`parent_chain.md`](parent_chain.md). Colonnes : `services/total_emissions.py`. Tests : `tests/services/test_total_emissions.py`.

```
total = eec + el + ei + ep + etd + eu - eccs - esca - eccr
```

Les postes `eec`, `el`, `ei`, `ep`, `etd`, `eu`, `eccs`, `esca` et `eccr` du JSON sont les sommes sur ce chemin. `total` est la formule ci-dessus.

## Exemple

Trois actions, `leaf → middle → root`. Les postes absents du tableau valent 0. Ils se somment de la même façon.

| action | ei | ep | etd | eu | eccs | parent |
|--------|----|----|-----|----|------|--------|
| root   | 1  | 2  | 3   | 4  | 5    | —      |
| middle | 10 | 20 | 30  | 40 | 50   | root   |
| leaf   | 100| 200| 300 | 400| 500  | middle |

`total_emissions` de **leaf** = sommes du chemin leaf + middle + root :

```
ei=111, ep=222, etd=333, eu=444, eccs=555
total = 111+222+333+444-555 = 555
```

root ne cumule qu'elle-même (`total=5`). middle = root + middle (`total=55`).
