from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneContract, BiomethaneContractAmendment
from core.models import Entity
from core.tests_utils import setup_current_user

User = get_user_model()


class BiomethaneEntityConfigAmendmentViewSetTests(TestCase):
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

        self.contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            pap_contracted=50.0,
        )

        self.amendment_url = reverse("biomethane-contract-amendment-list")
        self.amendment_url += "?entity_id=" + str(self.producer_entity.id)

        self.test_file = SimpleUploadedFile("test_amendment.pdf", b"fake pdf content", content_type="application/pdf")

    def test_create_amendment_single_object(self):
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": ["CMAX_PAP_UPDATE"],
            "amendment_file": self.test_file,
        }

        response = self.client.post(self.amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        amendment = BiomethaneContractAmendment.objects.get(contract=self.contract)
        self.assertEqual(amendment.amendment_object, ["CMAX_PAP_UPDATE"])
        self.assertEqual(str(amendment.signature_date), "2025-08-08")
        self.assertEqual(str(amendment.effective_date), "2025-08-15")

    def test_create_amendment_multiple_objects(self):
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": ["CMAX_PAP_UPDATE", "INPUT_BONUS_UPDATE"],
            "amendment_file": self.test_file,
        }

        response = self.client.post(self.amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        amendment = BiomethaneContractAmendment.objects.get(contract=self.contract)
        self.assertEqual(amendment.amendment_object, ["CMAX_PAP_UPDATE", "INPUT_BONUS_UPDATE"])

    def test_create_amendment_with_other_requires_details(self):
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": ["OTHER"],
            "amendment_file": self.test_file,
            # Manque amendment_details
        }

        response = self.client.post(self.amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amendment_details", response.data)

    def test_create_amendment_with_other_and_details(self):
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": ["OTHER"],
            "amendment_file": self.test_file,
            "amendment_details": "Modification spécifique non listée",
        }

        response = self.client.post(self.amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        amendment = BiomethaneContractAmendment.objects.get(contract=self.contract)
        self.assertEqual(amendment.amendment_object, ["OTHER"])
        self.assertEqual(amendment.amendment_details, "Modification spécifique non listée")

    def test_create_amendment_missing_required_fields(self):
        data = {
            "signature_date": "2025-08-08",
            # Manque effective_date, amendment_object, amendment_file
        }

        response = self.client.post(self.amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("effective_date", response.data)
        self.assertIn("amendment_object", response.data)
        self.assertIn("amendment_file", response.data)

    def test_create_amendment_invalid_object_choice(self):
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": ["INVALID_CHOICE"],
            "amendment_file": self.test_file,
        }

        response = self.client.post(self.amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amendment_object", response.data)

    def test_create_amendment_without_contract(self):
        entity_without_contract = Entity.objects.create(
            name="Producer Without Contract",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        setup_current_user(
            self,
            "tester2@carbure.local",
            "Tester2",
            "gogogo2",
            [(entity_without_contract, "RW")],
        )

        amendment_url = reverse("biomethane-contract-amendment-list")
        amendment_url += "?entity_id=" + str(entity_without_contract.id)

        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": ["CMAX_PAP_UPDATE"],
            "amendment_file": self.test_file,
        }

        response = self.client.post(amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contract", response.data)

    def test_list_amendments(self):
        BiomethaneContractAmendment.objects.create(
            contract=self.contract,
            signature_date=date(2025, 7, 1),
            effective_date=date(2025, 7, 15),
            amendment_object=["CMAX_PAP_UPDATE"],
            amendment_file=self.test_file,
        )

        BiomethaneContractAmendment.objects.create(
            contract=self.contract,
            signature_date=date(2025, 8, 1),
            effective_date=date(2025, 8, 15),
            amendment_object=["EFFECTIVE_DATE", "OTHER"],
            amendment_file=self.test_file,
            amendment_details="Détails spécifiques",
        )

        response = self.client.get(self.amendment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

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

        amendment_url = reverse("biomethane-contract-amendment-list")
        amendment_url += "?entity_id=" + str(wrong_entity.id)

        response = self.client.get(amendment_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": ["CMAX_PAP_UPDATE"],
            "amendment_file": self.test_file,
        }

        response = self.client.post(amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_empty_amendment_object_list(self):
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": [],
            "amendment_file": self.test_file,
        }

        response = self.client.post(self.amendment_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amendment_object", response.data)
