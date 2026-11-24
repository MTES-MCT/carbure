from functools import reduce
from operator import or_

from django.db import models
from django.db.models import Q

from traceability.models.action import Industry


class Tag(models.TextChoices):
    INDUSTRY = "industry", "Filière"


VALUES_PER_TYPE = {
    Tag.INDUSTRY: dict(Industry.choices),
}


def T(type: str, value: str):
    return Q(tags__type=type, tags__value=value)


def values_per_type_constraint(values_per_type):
    # par exemple, génére une condition du genre:
    # Q(type="industry", value__in=industries) | Q("nature", value__in=natures) | ...
    # pour l'instant, c'est une contrainte stricte qui rejette les valeurs non listées
    return models.CheckConstraint(
        condition=reduce(or_, (Q(type=tag_type, value__in=list(values)) for tag_type, values in values_per_type.items())),
        name="material_tag_values_per_type",
    )


class MaterialTag(models.Model):
    material = models.ForeignKey("traceability.Material", on_delete=models.CASCADE, related_name="tags")
    type = models.CharField(max_length=32, choices=Tag.choices)
    value = models.CharField(max_length=64, choices=VALUES_PER_TYPE)

    class Meta:
        db_table = "material_tag"
        constraints = [
            values_per_type_constraint(VALUES_PER_TYPE),
            models.UniqueConstraint(fields=["material", "type", "value"], name="material_tag_unique"),
        ]
