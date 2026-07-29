from dataclasses import dataclass

from django.db.models import Q, Sum
from django.db.models.functions import Round

from biomethane.models import BiomethaneSupplyInput
from biomethane.services.supply_plan.volume import wet_matter_tonnage_expression

# Category labels from feedstocks/fixtures/import-intrants-biomethane.xlsx (typo kept as in source data).
CATEGORY_PRIMARY_CROPS = "Biomasse agricole - Cultures pour alimentaiton humaine ou animale (principales)"
CATEGORY_INTERMEDIATE_CROPS = "Biomasse agricole - Cultures intermédiaires"


def _compute_percentage(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return 0
    return round(numerator * 100.0 / denominator, 2)


@dataclass(frozen=True)
class SupplyPlanMetrics:
    total_gross_volume_tmb: float | None
    primary_crop_percentage: float | None
    intermediate_crop_percentage: float | None


def preload_supply_plan_metrics(producer_ids: list[int], year: int) -> dict[int, SupplyPlanMetrics]:
    """Aggregate gross supply input tonnage and crop shares per producer for a given year."""
    if not producer_ids:
        return {}

    gross_volume = wet_matter_tonnage_expression()
    rows = (
        BiomethaneSupplyInput.objects.filter(
            supply_plan__producer_id__in=producer_ids,
            supply_plan__year=year,
        )
        .values("supply_plan__producer_id")
        .annotate(
            total_gross_volume_tmb=Round(Sum(gross_volume), 2),
            primary_crop_gross_volume_tmb=Round(
                Sum(gross_volume, filter=Q(feedstock__classification__category=CATEGORY_PRIMARY_CROPS)),
                2,
            ),
            intermediate_crop_gross_volume_tmb=Round(
                Sum(gross_volume, filter=Q(feedstock__classification__category=CATEGORY_INTERMEDIATE_CROPS)),
                2,
            ),
        )
    )

    return {
        row["supply_plan__producer_id"]: SupplyPlanMetrics(
            total_gross_volume_tmb=row["total_gross_volume_tmb"],
            primary_crop_percentage=_compute_percentage(
                row["primary_crop_gross_volume_tmb"],
                row["total_gross_volume_tmb"],
            ),
            intermediate_crop_percentage=_compute_percentage(
                row["intermediate_crop_gross_volume_tmb"],
                row["total_gross_volume_tmb"],
            ),
        )
        for row in rows
    }
