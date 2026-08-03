"""
Volume-weighted P1 / P2 / P3 / P / Pef shares for declared supply inputs.

Business rules (single source of truth, applied in SQL):
- Proportions use wet matter tonnage (tMB), not dry matter (tMS).
- Coefficient comes from BiomethaneFeedstockTariffCoefficient
  (feedstock × tariff regime × collection_type).
- Regime is derived from the producer contract tariff_reference.
- collection_type is matched exactly: supply-input NULL maps to referential ""
  (unconditional rule). No matching row means no coefficient (still in denominator).
"""

from django.db.models import Case, CharField, F, FloatField, OuterRef, QuerySet, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce

from biomethane.models import BiomethaneFeedstockTariffCoefficient, BiomethaneSupplyInput
from biomethane.services.supply_plan.volume import wet_matter_tonnage_expression

Coeff = BiomethaneFeedstockTariffCoefficient

COEFFICIENTS = (Coeff.P1, Coeff.P2, Coeff.P3, Coeff.P, Coeff.PEF)


def compute_tariff_coefficient_proportions(
    queryset: QuerySet[BiomethaneSupplyInput], tariff_reference: str | None = None
) -> dict[str, float] | None:
    """
    Return {"p1": …, "p2": …, "p3": …, "p": …, "pef": …} as % of declared wet matter tonnage (tMB).

    When tariff_reference is omitted, each line uses its producer contract regime.
    When tariff_reference is provided, that regime applies to every line (override).

    Lines without a coefficient still weigh the denominator; they are not assigned to a bucket.

    Returns None when the feedstock tariff coefficient referential is empty (UI must hide proportions).
    """
    if not Coeff.objects.exists():
        return None

    if not queryset.exists():
        return _zeros()

    if tariff_reference is not None and not Coeff.regime_for_tariff_reference(tariff_reference):
        return _zeros()

    # 1. Tariff decree → regime (AT_2011 or AT_2020_PLUS), per line or overridden globally.
    queryset = _annotate_regime(queryset, tariff_reference)

    # 2. Referential lookup: feedstock × regime × collection_type.
    #    Supply-input NULL → "" to match unconditional referential rows.
    rows = (
        queryset.annotate(collection_key=Coalesce("collection_type", Value("")))
        .annotate(
            effective_coefficient=_effective_coefficient_subquery(),
            wet_matter_tonnage=wet_matter_tonnage_expression(),
        )
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

    # 3. Convert volumes to percentages (unclassified tonnage is in total but not in any bucket).
    total = rows["total"] or 0.0
    if not total:
        return _zeros()

    return {coeff.lower(): _percentage(rows[coeff.lower()] or 0.0, total) for coeff in COEFFICIENTS}


def _effective_coefficient_subquery():
    """Resolve coefficient for feedstock × regime × collection_key ("" = unconditional)."""
    return Subquery(
        Coeff.objects.filter(
            feedstock_id=OuterRef("feedstock_id"),
            regime=OuterRef("regime"),
            collection_type=OuterRef("collection_key"),
        ).values("coefficient")[:1],
        output_field=CharField(),
    )


def _annotate_regime(
    queryset: QuerySet[BiomethaneSupplyInput], tariff_reference: str | None
) -> QuerySet[BiomethaneSupplyInput]:
    """
    Annotate each line with the tariff decree regime used for coefficient lookup.

    When tariff_reference is provided, every line uses that override.
    Otherwise, regime is derived from each producer's contract.
    """
    if tariff_reference is not None:
        calculated_regime = Coeff.regime_for_tariff_reference(tariff_reference)
        return queryset.annotate(regime=Value(calculated_regime, output_field=CharField()))

    regime_whens = [
        When(
            supply_plan__producer__biomethane_contract__tariff_reference=ref,
            then=Value(regime),
        )
        for ref, regime in Coeff.TARIFF_REFERENCE_TO_REGIME.items()
    ]
    return queryset.annotate(
        regime=Case(*regime_whens, default=Value(None), output_field=CharField()),
    )


def _percentage(part: float, total: float) -> float:
    return round(part / total * 100, 2)


def _zeros() -> dict[str, float]:
    return {coeff.lower(): 0.0 for coeff in COEFFICIENTS}
