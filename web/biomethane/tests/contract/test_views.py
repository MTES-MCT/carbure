from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories.contract import BiomethaneContractFactory, BiomethaneSignedContractFactory
from biomethane.factories.production_unit import BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneContract
from core.models import Department, Entity, ExternalAdminRights
from core.tests_utils import setup_current_user
from entity.models import EntityScope

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

    @patch(
        "biomethane.services.annual_declaration.BiomethaneAnnualDeclarationService.get_current_declaration_year",
        return_value=2025,
    )
    def test_retrieve_contract_restricted_access_returns_only_specific_fields(self, _):
        """Test restricted contract access returns only specific fields."""
        department = Department.objects.create(code_dept="75", name="Paris")
        BiomethaneProductionUnitFactory.create(producer=self.producer_entity, department=department)
        BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
            pap_contracted=50.0,
            has_complementary_investment_aid=True,
            complementary_aid_organisms=[BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME],
            effective_date=date(2021, 1, 1),
        )

        restricted_entity = Entity.objects.create(name="Restricted Admin", entity_type=Entity.EXTERNAL_ADMIN)
        ExternalAdminRights.objects.create(entity=restricted_entity, right=ExternalAdminRights.ADEME)
        EntityScope.objects.create(
            entity=restricted_entity,
            content_type=ContentType.objects.get_for_model(Department),
            object_id=department.id,
        )

        setup_current_user(
            self,
            "restricted-admin@carbure.local",
            "Restricted Admin",
            "gogogo",
            [(restricted_entity, "RW")],
        )

        response = self.client.get(
            self.contract_url, {"entity_id": restricted_entity.id, "producer_id": self.producer_entity.id}
        )

        watched_fields = ["tariff_reference", "installation_category"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(watched_fields))
