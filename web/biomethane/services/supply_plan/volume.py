"""
Convert supply input volumes to wet matter tonnage (tMB).

Single source of truth for tMS → tMB conversion:

    tMB = tMS × 100 / dry_matter_ratio_percent

where ``dry_matter_ratio_percent`` is a percentage in [0, 100] (e.g. 24 means 24 %).
"""

from django.db.models import Case, F, FloatField, QuerySet, Value, When
from django.db.models.functions import Round

from biomethane.models import BiomethaneSupplyInput

VOLUME_TMB_ANNOTATION = "volume_tmb"


def wet_matter_tonnage_expression():
    """
    ORM expression: declared volume converted to wet matter tonnage (tMB).

    - WET: volume is already tMB.
    - DRY: tMB = tMS × 100 / dry_matter_ratio_percent.
    - Otherwise: NULL (line excluded from aggregates).
    """
    return Case(
        When(material_unit=BiomethaneSupplyInput.WET, then=F("volume")),
        When(
            material_unit=BiomethaneSupplyInput.DRY,
            dry_matter_ratio_percent__gt=0,
            then=F("volume") * 100.0 / F("dry_matter_ratio_percent"),
        ),
        default=Value(None),
        output_field=FloatField(),
    )


def annotate_volume_tmb(queryset: QuerySet[BiomethaneSupplyInput]) -> QuerySet[BiomethaneSupplyInput]:
    """Annotate each supply input with rounded wet matter tonnage (volume_tmb)."""
    return queryset.annotate(**{VOLUME_TMB_ANNOTATION: Round(wet_matter_tonnage_expression(), 2)})
