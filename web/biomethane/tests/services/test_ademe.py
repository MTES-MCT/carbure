from datetime import date
from unittest.mock import patch

from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models import BiomethaneContract
from biomethane.services.admin.ademe import AdemeService
from core.models import Entity


class AdemeServiceTests(TestCase):
    def setUp(self):
        self.producer = Entity.objects.create(
            name="Producer Test",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    @patch("biomethane.services.admin.ademe.AdemeService.get_ademe_min_effective_year", return_value=2021)
    def test_get_ademe_contract_filter_builds_expected_filter(self, _):
        contract_filter = AdemeService.get_ademe_contract_filter("producer__biomethane_contract__")

        self.assertEqual(
            contract_filter.children,
            [
                (
                    "producer__biomethane_contract__complementary_aid_organisms__contains",
                    [BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME],
                ),
                ("producer__biomethane_contract__effective_date__year__gte", 2021),
            ],
        )

    def test_get_contract_from_object_returns_contract_for_contract_instance(self):
        contract = BiomethaneContractFactory.create(producer=self.producer)

        result = AdemeService.get_contract_from_object(contract)

        self.assertEqual(result, contract)

    def test_get_contract_from_object_returns_none_without_related_contract(self):
        class DummyObject:
            producer = None

        result = AdemeService.get_contract_from_object(DummyObject())

        self.assertIsNone(result)

    @patch("biomethane.services.admin.ademe.AdemeService.get_ademe_min_effective_year", return_value=2021)
    def test_is_allowed_to_access_object_true_when_ademe_and_effective_year_is_in_scope(self, _):
        contract = BiomethaneContractFactory.create(
            producer=self.producer,
            has_complementary_investment_aid=True,
            complementary_aid_organisms=[BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME],
            effective_date=date(2021, 1, 1),
        )

        result = AdemeService.is_allowed_to_access_object(contract)

        self.assertTrue(result)

    @patch("biomethane.services.admin.ademe.AdemeService.get_ademe_min_effective_year", return_value=2021)
    def test_is_allowed_to_access_object_false_when_contract_without_ademe_aid(self, _):
        contract = BiomethaneContractFactory.create(
            producer=self.producer,
            has_complementary_investment_aid=True,
            complementary_aid_organisms=[BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_REGION],
            effective_date=date(2021, 1, 1),
        )

        result = AdemeService.is_allowed_to_access_object(contract)

        self.assertFalse(result)

    def test_is_allowed_to_access_object_false_when_no_contract(self):
        class DummyObject:
            producer = None

        result = AdemeService.is_allowed_to_access_object(DummyObject())

        self.assertFalse(result)

    @patch("biomethane.services.admin.ademe.AdemeService.get_ademe_min_effective_year", return_value=2021)
    def test_is_allowed_to_access_object_false_when_effective_year_is_not_in_scope(self, _):
        contract = BiomethaneContractFactory.create(
            producer=self.producer,
            has_complementary_investment_aid=True,
            complementary_aid_organisms=[BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME],
            effective_date=date(2020, 1, 1),
        )

        result = AdemeService.is_allowed_to_access_object(contract)

        self.assertFalse(result)
