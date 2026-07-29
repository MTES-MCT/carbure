from django.db.models import Sum
from django.db.models.functions import Round
from django.test import TestCase

from biomethane.factories import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.models import BiomethaneSupplyInput
from biomethane.services.supply_plan.volume import annotate_volume_tmb, wet_matter_tonnage_expression
from core.models import Entity


class WetMatterTonnageExpressionTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.producer = Entity.objects.create(
            name="Test Producer Volume",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.supply_plan = BiomethaneSupplyPlanFactory.create(producer=self.producer)

    def test_aggregate_converts_dry_and_sums_wet(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            material_unit=BiomethaneSupplyInput.WET,
            dry_matter_ratio_percent=None,
            volume=100.0,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            material_unit=BiomethaneSupplyInput.DRY,
            dry_matter_ratio_percent=24.0,
            volume=200.0,
        )

        total = (
            BiomethaneSupplyInput.objects.filter(supply_plan=self.supply_plan)
            .aggregate(total=Round(Sum(wet_matter_tonnage_expression()), 2))
            .get("total")
        )

        # 100 tMB + 200 × 100 / 24 = 933.33
        self.assertEqual(total, 933.33)

    def test_annotate_volume_tmb(self):
        dry_input = BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            material_unit=BiomethaneSupplyInput.DRY,
            dry_matter_ratio_percent=24.0,
            volume=200.0,
        )

        annotated = annotate_volume_tmb(BiomethaneSupplyInput.objects.filter(pk=dry_input.pk)).get()
        # 200 × 100 / 24 = 833.33
        self.assertEqual(annotated.volume_tmb, 833.33)
