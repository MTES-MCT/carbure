"""Unit tests for supply_plan.tariff_coefficient service."""

from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.factories.supply_plan import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.models import BiomethaneFeedstockTariffCoefficient, BiomethaneSupplyInput
from biomethane.services.supply_plan.tariff_coefficient import (
    feedstock_requires_local_collection_for_coefficient,
    resolve_tariff_coefficient,
)
from core.models import MatierePremiere


class ResolveTariffCoefficientTests(TestCase):
    def setUp(self):
        self.feedstock_mais = MatierePremiere.objects.create(
            name="Maïs",
            name_en="Corn",
            code="MAIS",
            is_methanogenic=True,
        )
        self.feedstock_huiles = MatierePremiere.objects.create(
            name="Huiles animales",
            name_en="Animal oils",
            code="HUILES-ALIMENTAIRES-USAGEES-DORIGINE-ANIMALE",
            is_methanogenic=True,
        )
        BiomethaneFeedstockTariffCoefficient.objects.create(
            feedstock=self.feedstock_mais,
            regime=BiomethaneFeedstockTariffCoefficient.AT_2011,
            coefficient=BiomethaneFeedstockTariffCoefficient.P2,
        )
        BiomethaneFeedstockTariffCoefficient.objects.create(
            feedstock=self.feedstock_mais,
            regime=BiomethaneFeedstockTariffCoefficient.AT_2020_PLUS,
            coefficient=BiomethaneFeedstockTariffCoefficient.P,
        )
        BiomethaneFeedstockTariffCoefficient.objects.create(
            feedstock=self.feedstock_huiles,
            regime=BiomethaneFeedstockTariffCoefficient.AT_2011,
            coefficient=BiomethaneFeedstockTariffCoefficient.P1,
        )

        self.supply_plan = BiomethaneSupplyPlanFactory.create()
        BiomethaneContractFactory.create(
            producer=self.supply_plan.producer,
            tariff_reference="2011",
        )

    def test_resolves_coefficient_for_standard_feedstock_at_2011(self):
        supply_input = BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_mais,
        )
        self.assertEqual(resolve_tariff_coefficient(supply_input), BiomethaneFeedstockTariffCoefficient.P2)

    def test_resolves_coefficient_for_at_2020_plus_regime(self):
        self.supply_plan.producer.biomethane_contract.tariff_reference = "2021"
        self.supply_plan.producer.biomethane_contract.save(update_fields=["tariff_reference"])
        supply_input = BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_mais,
        )
        self.assertEqual(resolve_tariff_coefficient(supply_input), BiomethaneFeedstockTariffCoefficient.P)

    def test_explicit_tariff_reference_overrides_contract(self):
        supply_input = BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_mais,
        )
        self.assertEqual(
            resolve_tariff_coefficient(supply_input, tariff_reference="2023"),
            BiomethaneFeedstockTariffCoefficient.P,
        )

    def test_returns_none_without_feedstock(self):
        supply_input = BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=None,
        )
        self.assertIsNone(resolve_tariff_coefficient(supply_input))

    def test_returns_none_without_referential_row(self):
        other = MatierePremiere.objects.create(
            name="Autre",
            name_en="Other",
            code="AUTRE-INTRANT-SANS-COEFF",
            is_methanogenic=True,
        )
        supply_input = BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=other,
        )
        self.assertIsNone(resolve_tariff_coefficient(supply_input))

    def test_collection_type_feedstock_requires_local(self):
        supply_input = BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_huiles,
            collection_type=BiomethaneSupplyInput.PRIVATE,
        )
        self.assertIsNone(resolve_tariff_coefficient(supply_input))

    def test_collection_type_feedstock_local_returns_coefficient(self):
        supply_input = BiomethaneSupplyInputFactory.create(
            supply_plan=self.supply_plan,
            feedstock=self.feedstock_huiles,
            collection_type=BiomethaneSupplyInput.LOCAL,
        )
        self.assertEqual(resolve_tariff_coefficient(supply_input), BiomethaneFeedstockTariffCoefficient.P1)

    def test_feedstock_requires_local_collection_helper(self):
        self.assertFalse(feedstock_requires_local_collection_for_coefficient(self.feedstock_mais))
        self.assertTrue(feedstock_requires_local_collection_for_coefficient(self.feedstock_huiles))
