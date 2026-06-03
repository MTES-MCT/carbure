"""Tests for supply_plan.tariff_coefficient proportions."""

from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.factories.supply_plan import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.models import BiomethaneFeedstockTariffCoefficient, BiomethaneSupplyInput
from biomethane.services.supply_plan.tariff_coefficient import compute_tariff_coefficient_proportions
from core.models import MatierePremiere

Coeff = BiomethaneFeedstockTariffCoefficient


class TariffCoefficientProportionsTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.supply_plan = BiomethaneSupplyPlanFactory.create()
        BiomethaneContractFactory.create(producer=self.supply_plan.producer, tariff_reference="2011")

        self.feedstock_p1 = MatierePremiere.objects.create(
            name="Intrant P1",
            name_en="Feedstock P1",
            code="INTRANT-P1",
            is_methanogenic=True,
        )
        self.feedstock_p2 = MatierePremiere.objects.create(
            name="Intrant P2",
            name_en="Feedstock P2",
            code="INTRANT-P2",
            is_methanogenic=True,
        )
        self.feedstock_huiles = MatierePremiere.objects.create(
            name="Huiles animales",
            name_en="Animal oils",
            code="HUILES-ALIMENTAIRES-USAGEES-DORIGINE-ANIMALE",
            is_methanogenic=True,
        )
        Coeff.objects.create(feedstock=self.feedstock_p1, regime=Coeff.AT_2011, coefficient=Coeff.P1)
        Coeff.objects.create(feedstock=self.feedstock_p2, regime=Coeff.AT_2011, coefficient=Coeff.P2)
        Coeff.objects.create(feedstock=self.feedstock_p2, regime=Coeff.AT_2020_PLUS, coefficient=Coeff.P)
        Coeff.objects.create(feedstock=self.feedstock_huiles, regime=Coeff.AT_2011, coefficient=Coeff.P1)

    def _inputs(self):
        return self.supply_plan.supply_inputs.all()

    def test_volume_weighted_percentages(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p1,
            volume=300,
            material_unit=BiomethaneSupplyInput.WET,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p2,
            volume=700,
            material_unit=BiomethaneSupplyInput.WET,
        )

        result = compute_tariff_coefficient_proportions(self._inputs())

        self.assertEqual(result, {"p1": 30.0, "p2": 70.0, "p3": 0.0, "p": 0.0, "pef": 0.0})

    def test_ignores_lines_without_volume(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p1,
            volume=100,
            material_unit=BiomethaneSupplyInput.WET,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p2,
            volume=None,
            material_unit=BiomethaneSupplyInput.WET,
        )

        self.assertEqual(compute_tariff_coefficient_proportions(self._inputs())["p1"], 100.0)

    def test_unclassified_tonnage_only_in_denominator(self):
        other = MatierePremiere.objects.create(
            name="Sans coeff",
            name_en="No coeff",
            code="NO-COEFF",
            is_methanogenic=True,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p1,
            volume=400,
            material_unit=BiomethaneSupplyInput.WET,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=other,
            volume=600,
            material_unit=BiomethaneSupplyInput.WET,
        )

        self.assertEqual(compute_tariff_coefficient_proportions(self._inputs())["p1"], 40.0)

    def test_regime_follows_contract_tariff_reference(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p2,
            volume=100,
            material_unit=BiomethaneSupplyInput.WET,
        )
        self.supply_plan.producer.biomethane_contract.tariff_reference = "2023"
        self.supply_plan.producer.biomethane_contract.save(update_fields=["tariff_reference"])

        self.assertEqual(compute_tariff_coefficient_proportions(self._inputs())["p"], 100.0)

    def test_explicit_tariff_reference_overrides_contract(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p2,
            volume=100,
            material_unit=BiomethaneSupplyInput.WET,
        )

        result = compute_tariff_coefficient_proportions(self._inputs(), tariff_reference="2023")

        self.assertEqual(result["p"], 100.0)

    def test_private_collection_type_excludes_coefficient(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_huiles,
            collection_type=BiomethaneSupplyInput.PRIVATE,
            volume=100,
            material_unit=BiomethaneSupplyInput.WET,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_huiles,
            collection_type=BiomethaneSupplyInput.LOCAL,
            volume=100,
            material_unit=BiomethaneSupplyInput.WET,
        )

        result = compute_tariff_coefficient_proportions(self._inputs())

        self.assertEqual(result["p1"], 50.0)

    def test_empty_plan_returns_zeros(self):
        self.assertEqual(
            compute_tariff_coefficient_proportions(BiomethaneSupplyInput.objects.none()),
            {"p1": 0.0, "p2": 0.0, "p3": 0.0, "p": 0.0, "pef": 0.0},
        )

    def test_converts_dry_matter_tonnage_to_wet_matter(self):
        """100 tMS at 40% MS → 250 tMB; proportions are on wet matter (tMB)."""
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p1,
            volume=100,
            material_unit=BiomethaneSupplyInput.DRY,
            dry_matter_ratio_percent=40,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p2,
            volume=50,
            material_unit=BiomethaneSupplyInput.WET,
        )

        result = compute_tariff_coefficient_proportions(self._inputs())

        # total tMB = 250 + 50 = 300
        self.assertEqual(result["p1"], 83.33)
        self.assertEqual(result["p2"], 16.67)

    def test_ignores_dry_lines_without_ratio(self):
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p1,
            volume=100,
            material_unit=BiomethaneSupplyInput.DRY,
            dry_matter_ratio_percent=None,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_p2,
            volume=50,
            material_unit=BiomethaneSupplyInput.WET,
        )

        result = compute_tariff_coefficient_proportions(self._inputs())

        self.assertEqual(result["p2"], 100.0)
