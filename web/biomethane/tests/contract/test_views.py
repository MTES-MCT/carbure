from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories.contract import BiomethaneContractFactory, BiomethaneSignedContractFactory
from biomethane.models import BiomethaneContract
from biomethane.views.contract.contract import BiomethaneContractViewSet
from core.models import Entity
from core.tests_utils import setup_current_user

User = get_user_model()


class BiomethaneContractViewsTests(TestCase):
    """Tests for biomethane contract management views."""

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.buyer_entity = Entity.objects.create(
            name="Test Buyer",
            entity_type=Entity.OPERATOR,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.producer_entity, "RW")],
        )

        self.contract_url = reverse("biomethane-contract")
        self.base_params = {"entity_id": self.producer_entity.id}

    @patch("biomethane.views.contract.contract.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that write actions are correctly defined"""
        viewset = BiomethaneContractViewSet()
        viewset.action = "retrieve"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with(["upsert"], "retrieve")

    def test_create_contract_tariff_rule_1(self):
        """Test creating a contract with tariff rule 1."""
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
        }

        response = self.client.put(self.contract_url, data, content_type="application/json", query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contract = BiomethaneContract.objects.get(producer=self.producer_entity)
        self.assertEqual(contract.tariff_reference, data["tariff_reference"])
        self.assertEqual(contract.buyer.id, data["buyer"])
        self.assertEqual(contract.installation_category, data["installation_category"])
        self.assertEqual(contract.cmax, data["cmax"])
        self.assertEqual(contract.cmax_annualized, data["cmax_annualized"])

    def test_create_contract_tariff_rule_2(self):
        """Test creating a contract with tariff rule 2."""
        data = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "pap_contracted": 50.0,
        }

        response = self.client.put(self.contract_url, data, content_type="application/json", query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contract = BiomethaneContract.objects.get(producer=self.producer_entity)
        self.assertEqual(contract.tariff_reference, data["tariff_reference"])
        self.assertEqual(contract.buyer.id, data["buyer"])
        self.assertEqual(contract.pap_contracted, data["pap_contracted"])

    def test_list_contract_exists(self):
        """Test retrieving an existing contract."""
        BiomethaneContractFactory.create(
            producer=self.producer_entity, buyer=self.buyer_entity, tariff_reference="2021", pap_contracted=50.0
        )

        response = self.client.get(self.contract_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["producer"], self.producer_entity.id)
        self.assertEqual(response.data["buyer"], self.buyer_entity.id)

    def test_patch_contract_basic_fields(self):
        """Test updating basic contract fields."""
        contract = BiomethaneContractFactory.create(
            producer=self.producer_entity, buyer=self.buyer_entity, tariff_reference="2021", pap_contracted=50.0
        )

        data = {"pap_contracted": 75.0}

        response = self.client.put(self.contract_url, data, content_type="application/json", query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contract.refresh_from_db()
        self.assertEqual(contract.pap_contracted, 75.0)

    @patch("biomethane.serializers.contract.contract.check_fields_required", return_value=None)
    def test_patch_contract_signed_cannot_update_contract_fields(self, _):
        """Test that certain fields cannot be modified on a signed contract."""
        BiomethaneSignedContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            pap_contracted=50.0,
            signature_date=date.today(),
            effective_date=date.today(),
        )

        data = {
            "signature_date": date(2025, 1, 1),
            "effective_date": date(2025, 1, 1),
        }

        response = self.client.put(self.contract_url, data, content_type="application/json", query_params=self.base_params)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("signature_date", response.data)
        self.assertIn("effective_date", response.data)
