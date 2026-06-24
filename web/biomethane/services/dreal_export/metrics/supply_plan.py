from dataclasses import dataclass

from django.db.models import Case, F, FloatField, Sum, Value, When
from django.db.models.functions import Round

from biomethane.models import BiomethaneSupplyInput


def _gross_volume_tmb_expression():
    """Convert each supply input volume to gross matter tonnage (tMB)."""
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


@dataclass(frozen=True)
class SupplyPlanMetrics:
    total_gross_volume_tmb: float | None


def preload_supply_plan_metrics(producer_ids: list[int], year: int) -> dict[int, SupplyPlanMetrics]:
    """Aggregate gross supply input tonnage per producer for a given year."""
    if not producer_ids:
        return {}

    rows = (
        BiomethaneSupplyInput.objects.filter(
            supply_plan__producer_id__in=producer_ids,
            supply_plan__year=year,
        )
        .values("supply_plan__producer_id")
        .annotate(total_gross_volume_tmb=Round(Sum(_gross_volume_tmb_expression()), 2))
    )

    return {
        row["supply_plan__producer_id"]: SupplyPlanMetrics(total_gross_volume_tmb=row["total_gross_volume_tmb"])
        for row in rows
    }
