"""
Volume-weighted P1 / P2 / P3 / P / Pef shares for declared supply inputs.

Business rules (single source of truth, applied in SQL):
- Proportions use wet matter tonnage (tMB), not dry matter (tMS).
- Coefficient comes from BiomethaneFeedstockTariffCoefficient
  (feedstock x tariff regime x collection_type).
- Regime is derived from the producer contract tariff_reference.
- collection_type is matched exactly against the referential ("" = unconditional rule).
  No matching row means no coefficient (still in denominator).
"""

from django.db.models import Case, CharField, F, FloatField, OuterRef, QuerySet, Subquery, Sum, Value, When

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

    # 1. Annotate each line with its wet matter tonnage and effective coefficient.
    queryset = _annotate_tonnages(queryset, tariff_reference)
    rows = queryset.aggregate(**_tonnage_aggregates())

    # 2. Aggregate wet matter tonnages by coefficient.
    total = rows["total"] or 0.0
    if not total:
        return _zeros()

    return {coeff.lower(): _percentage(rows[coeff.lower()] or 0.0, total) for coeff in COEFFICIENTS}


def compute_tariff_coefficient_summaries(queryset: QuerySet[BiomethaneSupplyInput]):
    """
    Return proportions and wet tonnages grouped by producer and supply plan year.

    Example:
    {
        (42, 2025): {
            "proportions": {"p1": 50.0, "p2": 10.0, "p3": 0.0, "p": 0.0, "pef": 0.0},
            "tonnages": {"total": 500.0, "p1": 250.0, "p2": 50.0, "p3": 0.0, "p": 0.0, "pef": 0.0},
        }
    }
    """
    if not Coeff.objects.exists():
        return None

    rows = (
        _annotate_tonnages(queryset)
        .order_by()
        .values("supply_plan__producer_id", "supply_plan__year")
        .annotate(**_tonnage_aggregates())
    )
    result = {}
    for row in rows:
        tonnages = {"total": row["total"] or 0.0}
        tonnages.update({coeff.lower(): row[coeff.lower()] or 0.0 for coeff in COEFFICIENTS})
        proportions = {coeff.lower(): _percentage(tonnages[coeff.lower()], tonnages["total"]) for coeff in COEFFICIENTS}
        result[(row["supply_plan__producer_id"], row["supply_plan__year"])] = {
            "proportions": proportions,
            "tonnages": tonnages,
        }
    return result


def _annotate_tonnages(queryset, tariff_reference=None):
    return (
        _annotate_regime(queryset, tariff_reference)
        .annotate(
            effective_coefficient=_effective_coefficient_subquery(),
            wet_matter_tonnage=wet_matter_tonnage_expression(),
        )
        .filter(wet_matter_tonnage__gt=0)
    )


def _tonnage_aggregates():
    return {
        "total": Sum("wet_matter_tonnage"),
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
    }


def _effective_coefficient_subquery():
    """Resolve coefficient for feedstock x regime x collection_type ("" = unconditional)."""
    return Subquery(
        Coeff.objects.filter(
            feedstock_id=OuterRef("feedstock_id"),
            regime=OuterRef("regime"),
            collection_type=OuterRef("collection_type"),
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
