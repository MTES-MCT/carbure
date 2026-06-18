"""
Volume-weighted share of primary crops in declared supply inputs (wet matter tonnage, tMB).

Numerator: tMB of lines whose feedstock classification is a primary crop (see feedstocks rules).
Denominator: total declared tMB (same basis as tariff coefficient proportions).
"""

from django.db.models import Case, F, FloatField, Sum, Value, When

from biomethane.services.supply_plan.tariff_coefficient import (
    _percentage,
    _wet_matter_tonnage_expression,
)
from feedstocks.models.classification import CATEGORY_PRIMARY_CROPS


def compute_primary_crop_proportion(queryset) -> float:
    """Return primary crop tonnage as % of total declared wet matter tonnage (tMB)."""
    if not queryset.exists():
        return 0.0

    wet_tonnage = _wet_matter_tonnage_expression()
    rows = (
        queryset.annotate(wet_matter_tonnage=wet_tonnage)
        .filter(wet_matter_tonnage__gt=0)
        .aggregate(
            total=Sum("wet_matter_tonnage"),
            primary=Sum(
                Case(
                    When(feedstock__classification__category=CATEGORY_PRIMARY_CROPS, then=F("wet_matter_tonnage")),
                    default=Value(0.0),
                    output_field=FloatField(),
                )
            ),
        )
    )

    total = rows["total"] or 0.0
    if not total:
        return 0.0

    return _percentage(rows["primary"] or 0.0, total)
