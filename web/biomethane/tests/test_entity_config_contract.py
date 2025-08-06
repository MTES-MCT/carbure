from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneEntityConfigContract
from core.models import Entity
from core.tests_utils import setup_current_user

User = get_user_model()


class BiomethaneEntityConfigContractViewSetTests(TestCase):
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

        self.contract_url = reverse("biomethane-entity-config-contract")
        self.contract_url += "?entity_id=" + str(self.producer_entity.id)

    def test_create_contract_tariff_rule_1(self):
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneEntityConfigContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
        }

        response = self.client.post(self.contract_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(BiomethaneEntityConfigContract.objects.filter(entity=self.producer_entity).exists())

        contract = BiomethaneEntityConfigContract.objects.get(entity=self.producer_entity)
        self.assertEqual(contract.tariff_reference, "2011")
        self.assertEqual(contract.buyer_id, self.buyer_entity.id)
        self.assertEqual(contract.cmax, 100.0)

    def test_create_contract_tariff_rule_2(self):
        data = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 50.0,
        }

        response = self.client.post(self.contract_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contract = BiomethaneEntityConfigContract.objects.get(entity=self.producer_entity)
        self.assertEqual(contract.tariff_reference, "2021")
        self.assertEqual(contract.pap_contracted, 50.0)

    def test_create_contract_missing_required_fields_rule_1(self):
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            # Missing: installation_category, cmax, cmax_annualized
        }

        response = self.client.post(self.contract_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("installation_category", response.data)
        self.assertIn("cmax", response.data)
        self.assertIn("cmax_annualized", response.data)

    def test_create_contract_cmax_annualized_validation(self):
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneEntityConfigContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": True,
            # Missing: cmax_annualized_value
        }

        response = self.client.post(self.contract_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cmax_annualized_value", response.data)

    def test_list_contract_exists(self):
        BiomethaneEntityConfigContract.objects.create(
            entity=self.producer_entity, buyer=self.buyer_entity, tariff_reference="2021", pap_contracted=50.0
        )

        response = self.client.get(self.contract_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["entity"], self.producer_entity.id)
        self.assertEqual(response.data["buyer"], self.buyer_entity.id)

    def test_patch_contract_basic_fields(self):
        contract = BiomethaneEntityConfigContract.objects.create(
            entity=self.producer_entity, buyer=self.buyer_entity, tariff_reference="2021", pap_contracted=50.0
        )

        data = {"pap_contracted": 75.0}

        response = self.client.patch(self.contract_url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contract.refresh_from_db()
        self.assertEqual(contract.pap_contracted, 75.0)

    def test_patch_contract_signed_cannot_update_contract_fields(self):
        BiomethaneEntityConfigContract.objects.create(
            entity=self.producer_entity,
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

        response = self.client.patch(self.contract_url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("signature_date", response.data)
        self.assertIn("effective_date", response.data)

    def test_wrong_entity_type_access(self):
        wrong_entity = Entity.objects.create(
            name="Wrong Entity",
            entity_type=Entity.OPERATOR,
        )

        setup_current_user(
            self,
            "tester2@carbure.local",
            "Tester2",
            "gogogo2",
            [(wrong_entity, "RW")],
        )

        contract_url = reverse("biomethane-entity-config-contract")
        contract_url += "?entity_id=" + str(wrong_entity.id)

        response = self.client.get(contract_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(contract_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(contract_url, {}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
