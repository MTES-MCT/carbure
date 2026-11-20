# Proposition d’ajout de tags aux matières

Les matières premières peuvent être classées de plusieurs façons, selon les critères propres à chaque domaine. Comment représenter ces classifications dans la base de données ? Une option serait d’ajouter des colonnes à la table des matières, une autre serait de créer des tables liées.

Une autre piste serait d’associer plusieurs tags à une même matière. Cela permettrait d’ajouter de nouveaux types de tags au besoin et de combiner les tags pour filtrer la liste.

Les exemples ci-dessous partent de quelques situations déjà rencontrées ou qui pourraient se présenter. Ils donnent une idée de ce que permettrait le modèle. Les cas à couvrir et les détails de l’implémentation restent à discuter (genre utiliser des tags pour les codes UDB, bof bof).

## Modèle

Le champ `type` indique le critère de classement, par exemple la filière. Le champ `tag` contient la valeur de ce critère pour la matière. Ainsi, `type="industry"` et `tag="BF"` indiquent que la matière relève de la filière biocarburant. Une matière qui relève de deux filières aurait deux lignes `MaterialTag` de type `industry`, une par filière.

Le dict `TAGS_PER_TYPE` associe des types de tags à des choices Django, afin de rajouter un niveau de validation supplémentaire, qu'on devra implémenter soit comme de la validation de model Django, soit comme des contraintes MySQL directement sur la table.

```python
class Tag(models.TextChoices):
    INDUSTRY = "industry", "Filière"
    COMPATIBILITY = "compatibility", "Compatibilité"
    UDB = "udb", "UDB"


class Industry(models.TextChoices):
    BIOFUEL = "BF", "Biocarburant"
    BIOMETHANE = "BM", "Biométhane"


class Compatibility(models.TextChoices):
    DIESEL = "DIESEL", "Diésel"
    ALCOHOL = "ALCOHOL", "Alcool"


class MaterialTag(models.Model):
    TAGS_PER_TYPE = {
        Tag.INDUSTRY: dict(Industry.choices),
        Tag.COMPATIBILITY: dict(Compatibility.choices),
        # Tag.UDB => volontairement omis pour laisser la validation libre
    }

    material = models.ForeignKey("traceability.Material", on_delete=models.CASCADE, related_name="tags")
    type = models.CharField(max_length=32, choices=Tag.choices)
    tag = models.CharField(max_length=64, choices=TAGS_PER_TYPE)
```

## Ajout depuis Python

Une méthode toute simple sur le modèle `Material` : `.add_tag(type: str, tag: str)`

```python
material.add_tag(Tag.INDUSTRY, Industry.BIOFUEL)
material.add_tag(Tag.INDUSTRY, Industry.BIOMETHANE)

material.add_tag(Tag.COMPATIBILITY, Compatibility.DIESEL)

material.add_tag(Tag.UDB, "URWW017")
material.add_tag(Tag.UDB, "URWW043")
```

## Filtrage des matières

Cet exemple illustre une recherche qui combine deux tags, ici la filière biocarburant et la compatibilité Diésel.

```python
biodiesel_feedstocks = Material.objects.filter(
    T(Tag.INDUSTRY, Industry.BIOFUEL) & T(Tag.COMPATIBILITY, Compatibility.DIESEL)
)
```

Définition de la fonction `T` :

```python
def T(type: str, tag: str):
    return Q(tags__type=type, tags__tag=tag)
```

## Import depuis le CSV

Le CSV pourrait garder une ligne par matière et réserver une colonne à chaque type de tag. Dans l’extrait ci-dessous, plusieurs valeurs peuvent figurer dans la même cellule, séparées par des espaces. La colonne `industry` contient par exemple les codes `BF` et `BM`.

```csv
code,  [...], industry, compatibility, udb
COLZA, [...], BF BM,    DIESEL,        URWW017 URWW043
```
