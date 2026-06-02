"""
Volume-weighted P1 / P2 / P3 / P / Peff shares for declared supply inputs.

Business rules (single source of truth, applied in SQL):
- Proportions use wet matter tonnage (tMB), not dry matter (tMS).
- Coefficient comes from BiomethaneFeedstockTariffCoefficient (feedstock × tariff regime).
- Regime is derived from the producer contract tariff_reference.
- Some feedstocks only count when collection_type is LOCAL.
"""

from django.db.models import Case, CharField, F, FloatField, OuterRef, Q, Subquery, Sum, Value, When

from biomethane.models import BiomethaneFeedstockTariffCoefficient, BiomethaneSupplyInput
from biomethane.services.supply_plan.supply_input import COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES

Coeff = BiomethaneFeedstockTariffCoefficient

COEFFICIENTS = (Coeff.P1, Coeff.P2, Coeff.P3, Coeff.P, Coeff.PEFF)
LOCAL_COLLECTION = Q(feedstock__code__in=COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES)


def compute_tariff_coefficient_proportions(queryset, tariff_reference: str | None = None) -> dict[str, float]:
    """
    Return {"p1": …, "p2": …, "p3": …, "p": …, "peff": …} as % of declared wet matter tonnage (tMB).

    Lines without a coefficient still weigh the denominator; they are not assigned to a bucket.
    """
    if not queryset.exists():
        return _zeros()

    # 1. Contract tariff decree → regime (AT_2011 or AT_2020_PLUS).
    if tariff_reference is None:
        tariff_reference = queryset.values_list(
            "supply_plan__producer__biomethane_contract__tariff_reference",
            flat=True,
        ).first()

    regime = Coeff.regime_for_tariff_reference(tariff_reference)
    if not regime:
        return _zeros()

    # 2. Referential lookup: coefficient for each line's feedstock under this regime.
    referential = Subquery(
        Coeff.objects.filter(feedstock_id=OuterRef("feedstock_id"), regime=regime).values("coefficient")[:1],
        output_field=CharField(),
    )

    # 3. Apply local-collection rule: some feedstocks only get a coefficient when collection_type is LOCAL.
    effective = Case(
        When(LOCAL_COLLECTION & Q(collection_type=BiomethaneSupplyInput.LOCAL), then=referential),
        When(LOCAL_COLLECTION, then=Value(None, output_field=CharField())),
        default=referential,
        output_field=CharField(),
    )

    # 4. Convert each line to wet matter (tMB), then sum total and per-coefficient buckets.
    wet_tonnage = _wet_matter_tonnage_expression()
    rows = (
        queryset.annotate(effective_coefficient=effective, wet_matter_tonnage=wet_tonnage)
        .filter(wet_matter_tonnage__gt=0)
        .aggregate(
            total=Sum("wet_matter_tonnage"),
            **{
                coeff.lower(): Sum(
                    Case(
                        When(effective_coefficient=coeff, then=F("wet_matter_tonnage")),
                        default=Value(0.0),
                        output_field=FloatField(),
                    )
                )
                for coeff in COEFFICIENTS
            },
        )
    )

    # 5. Convert volumes to percentages (unclassified tonnage is in total but not in any bucket).
    total = rows["total"] or 0.0
    if not total:
        return _zeros()

    return {coeff.lower(): _pct(rows[coeff.lower()] or 0.0, total) for coeff in COEFFICIENTS}


def _wet_matter_tonnage_expression():
    """
    ORM expression: declared volume converted to wet matter tonnage (tMB).

    - WET: volume is already tMB.
    - DRY: tMB = tMS / (dry_matter_ratio_percent / 100).
    - Otherwise: NULL (line excluded from totals).
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


def _pct(part: float, total: float) -> float:
    return round(part / total * 100, 2)


def _zeros() -> dict[str, float]:
    return {coeff.lower(): 0.0 for coeff in COEFFICIENTS}
