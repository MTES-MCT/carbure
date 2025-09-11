from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneContract, BiomethaneContractAmendment
from core.models import Entity
from core.tests_utils import setup_current_user


class BiomethaneContractAmendmentViewSetTests(TestCase):
    def setUp(self):
        """Initial setup for tests"""
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

        # Create a base contract for amendments
        self.contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            pap_contracted=50.0,
        )

        self.amendment_list_url = reverse("biomethane-contract-amendment-list")
        self.amendment_create_url = reverse("biomethane-contract-amendment-list")
        self.base_params = {"entity_id": self.producer_entity.id}

        self.test_file = SimpleUploadedFile("test_amendment.pdf", b"fake pdf content", content_type="application/pdf")

    def test_list_amendments_empty(self):
        """Test listing amendments when none exist"""
        response = self.client.get(self.amendment_list_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_amendments_success(self):
        """Test successful listing of amendments"""
        # Create test amendments
        amendment1 = BiomethaneContractAmendment.objects.create(
            contract=self.contract,
            signature_date=date.today(),
            effective_date=date.today(),
            amendment_object=[BiomethaneContractAmendment.CMAX_PAP_UPDATE],
            amendment_file=self.test_file,
        )
        amendment2 = BiomethaneContractAmendment.objects.create(
            contract=self.contract,
            signature_date=date.today(),
            effective_date=date.today(),
            amendment_object=[BiomethaneContractAmendment.EFFECTIVE_DATE],
            amendment_file=self.test_file,
        )

        response = self.client.get(self.amendment_list_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

        # Check that both amendments are present
        amendment_ids = [result["id"] for result in response.data["results"]]
        self.assertIn(amendment1.id, amendment_ids)
        self.assertIn(amendment2.id, amendment_ids)

    def test_create_amendment_success(self):
        """Test successful creation of a new amendment"""

        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": [BiomethaneContractAmendment.CMAX_PAP_UPDATE],
            "amendment_file": self.test_file,
        }

        response = self.client.post(
            self.amendment_create_url,
            data,
            query_params=self.base_params,
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that the object was created in the database
        amendment = BiomethaneContractAmendment.objects.get(contract=self.contract)
        self.assertEqual(amendment.contract_id, self.contract.id)

    def test_create_amendment_missing_required_fields(self):
        """Test validation error when required fields are missing"""
        data = {
            "contract": self.contract.id,
            # Missing: signature_date, effective_date, amendment_object, amendment_file
        }

        response = self.client.post(
            self.amendment_create_url,
            data,
            query_params=self.base_params,
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("signature_date", response.data)
        self.assertIn("effective_date", response.data)
        self.assertIn("amendment_object", response.data)
        self.assertIn("amendment_file", response.data)

    def test_retrieve_amendment_success(self):
        """Test successful retrieval of a specific amendment"""
        amendment = BiomethaneContractAmendment.objects.create(
            contract=self.contract,
            signature_date=date.today(),
            effective_date=date.today(),
            amendment_object=[BiomethaneContractAmendment.CMAX_PAP_UPDATE],
            amendment_file=self.test_file,
        )

        amendment_detail_url = reverse("biomethane-contract-amendment-detail", kwargs={"pk": amendment.id})

        response = self.client.get(amendment_detail_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], amendment.id)
        self.assertEqual(response.data["contract"], self.contract.id)
        self.assertEqual(response.data["amendment_object"], [BiomethaneContractAmendment.CMAX_PAP_UPDATE])
        self.assertEqual(response.data["signature_date"], date.today().isoformat())
        self.assertEqual(response.data["effective_date"], date.today().isoformat())

    def test_retrieve_amendment_not_found(self):
        """Test 404 return when amendment doesn't exist"""
        amendment_detail_url = reverse("biomethane-contract-amendment-detail", kwargs={"pk": 99999})

        response = self.client.get(amendment_detail_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_amendment_invalid_amendment_object(self):
        """Test validation error for invalid amendment object"""
        data = {
            "contract": self.contract.id,
            "signature_date": date.today().isoformat(),
            "effective_date": date.today().isoformat(),
            "amendment_object": ["INVALID_TYPE"],
            "amendment_file": self.test_file,
        }

        response = self.client.post(
            self.amendment_create_url,
            data,
            query_params=self.base_params,
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amendment_object", response.data)

    def test_create_amendment_multiple_objects(self):
        """Test creating amendment with multiple amendment objects"""
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": [
                BiomethaneContractAmendment.CMAX_PAP_UPDATE,
                BiomethaneContractAmendment.INPUT_BONUS_UPDATE,
            ],
            "amendment_file": self.test_file,
        }

        response = self.client.post(self.amendment_create_url, data, query_params=self.base_params, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        amendment = BiomethaneContractAmendment.objects.get(contract=self.contract)
        self.assertEqual(len(amendment.amendment_object), 2)
        self.assertIn(BiomethaneContractAmendment.CMAX_PAP_UPDATE, amendment.amendment_object)
        self.assertIn(BiomethaneContractAmendment.INPUT_BONUS_UPDATE, amendment.amendment_object)

    def test_create_amendment_with_other_requires_details(self):
        """Test validation that amendment_details is required when amendment_object contains OTHER"""
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": [BiomethaneContractAmendment.OTHER],
            "amendment_file": self.test_file,
            # Missing amendment_details
        }

        response = self.client.post(self.amendment_create_url, data, query_params=self.base_params, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amendment_details", response.data)

    def test_create_amendment_with_other_and_details(self):
        """Test successful creation with OTHER and amendment_details"""
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": [BiomethaneContractAmendment.OTHER],
            "amendment_file": self.test_file,
            "amendment_details": "Modification spécifique non listée",
        }

        response = self.client.post(self.amendment_create_url, data, query_params=self.base_params, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        amendment = BiomethaneContractAmendment.objects.get(contract=self.contract)
        self.assertEqual(amendment.amendment_object, [BiomethaneContractAmendment.OTHER])
        self.assertEqual(amendment.amendment_details, "Modification spécifique non listée")

    def test_create_amendment_without_contract(self):
        """Test error when entity has no contract"""
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
        params = {"entity_id": entity_without_contract.id}

        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": [BiomethaneContractAmendment.CMAX_PAP_UPDATE],
            "amendment_file": self.test_file,
        }

        response = self.client.post(amendment_url, data, query_params=params, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contract", response.data)

    def test_empty_amendment_object_list(self):
        """Test validation error for empty amendment_object list"""
        data = {
            "signature_date": "2025-08-08",
            "effective_date": "2025-08-15",
            "amendment_object": [],  # Empty list
            "amendment_file": self.test_file,
        }

        response = self.client.post(self.amendment_create_url, data, query_params=self.base_params, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amendment_object", response.data)
