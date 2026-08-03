"""Tests for supply_plan.primary_crop_proportion."""

from django.test import TestCase

from biomethane.factories.supply_plan import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.models import BiomethaneSupplyInput
from biomethane.services.supply_plan.primary_crop_proportion import compute_primary_crop_proportion
from core.models import MatierePremiere
from feedstocks.models import Classification
from feedstocks.models.classification import CATEGORY_PRIMARY_CROPS


class PrimaryCropProportionTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.supply_plan = BiomethaneSupplyPlanFactory.create()
        self.classification_primary = Classification.objects.create(
            group="Biomasse agricole",
            category=CATEGORY_PRIMARY_CROPS,
            subcategory="Maïs",
        )
        self.classification_other = Classification.objects.create(
            group="Déchets",
            category="Déchets ménagers",
            subcategory="Autre",
        )
        self.feedstock_primary = MatierePremiere.objects.create(
            name="Maïs",
            name_en="Corn",
            code="MAIS-PRIMARY",
            is_methanogenic=True,
            classification=self.classification_primary,
        )
        self.feedstock_other = MatierePremiere.objects.create(
            name="Autre",
            name_en="Other",
            code="AUTRE-DECHET",
            is_methanogenic=True,
            classification=self.classification_other,
        )

    def _inputs(self):
        return self.supply_plan.supply_inputs.all()

    def test_volume_weighted_primary_crop_percentage(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_primary,
            volume=300,
            material_unit=BiomethaneSupplyInput.WET,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_other,
            volume=700,
            material_unit=BiomethaneSupplyInput.WET,
        )

        self.assertEqual(compute_primary_crop_proportion(self._inputs()), 30.0)

    def test_unclassified_tonnage_only_in_denominator(self):
        no_classification = MatierePremiere.objects.create(
            name="Sans classification",
            name_en="No class",
            code="NO-CLASS",
            is_methanogenic=True,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_primary,
            volume=400,
            material_unit=BiomethaneSupplyInput.WET,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=no_classification,
            volume=600,
            material_unit=BiomethaneSupplyInput.WET,
        )

        self.assertEqual(compute_primary_crop_proportion(self._inputs()), 40.0)

    def test_converts_dry_matter_to_wet_matter(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_primary,
            volume=100,
            material_unit=BiomethaneSupplyInput.DRY,
            dry_matter_ratio_percent=40,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_other,
            volume=50,
            material_unit=BiomethaneSupplyInput.WET,
        )

        # total tMB = 250 + 50 = 300 → primary = 83.33 %
        self.assertEqual(compute_primary_crop_proportion(self._inputs()), 83.33)

    def test_empty_plan_returns_zero(self):
        self.assertEqual(compute_primary_crop_proportion(BiomethaneSupplyInput.objects.none()), 0.0)
