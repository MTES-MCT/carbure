from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from biomethane.factories.contract import BiomethaneEntityConfigAmendmentFactory, BiomethaneSignedContractFactory
from biomethane.models import BiomethaneContractAmendment
from biomethane.serializers import BiomethaneContractAmendmentAddSerializer, BiomethaneContractAmendmentSerializer
from core.models import Entity


class BiomethaneContractAmendmentSerializerTests(TestCase):
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

        # Create a base contract for amendments
        self.contract = BiomethaneSignedContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            pap_contracted=50.0,
        )

        self.test_file = SimpleUploadedFile("test_amendment.pdf", b"fake pdf content", content_type="application/pdf")

        self.amendment = BiomethaneEntityConfigAmendmentFactory.create(
            contract=self.contract,
            amendment_object=[BiomethaneContractAmendment.CMAX_PAP_UPDATE],
        )

    def test_amendment_serializer_read(self):
        """Test reading amendment data with serializer"""
        serializer = BiomethaneContractAmendmentSerializer(self.amendment)
        data = serializer.data

        self.assertEqual(data["id"], self.amendment.id)
        self.assertEqual(data["contract"], self.contract.id)
        self.assertEqual(data["amendment_object"], [BiomethaneContractAmendment.CMAX_PAP_UPDATE])
        self.assertEqual(data["signature_date"], self.amendment.signature_date.isoformat())
        self.assertEqual(data["effective_date"], self.amendment.effective_date.isoformat())

    def test_amendment_add_serializer_valid_data(self):
        """Test creating amendment with valid data"""
        test_file = SimpleUploadedFile("new_amendment.pdf", b"fake pdf content", content_type="application/pdf")

        data = {
            "signature_date": date.today().isoformat(),
            "effective_date": date.today().isoformat(),
            "amendment_object": [BiomethaneContractAmendment.OTHER],
            "amendment_file": test_file,
            "amendment_details": "Modification spécifique non listée",
        }

        context = {"entity": self.producer_entity}
        serializer = BiomethaneContractAmendmentAddSerializer(data=data, context=context)

        self.assertTrue(serializer.is_valid())
        amendment = serializer.save()

        self.assertEqual(amendment.contract_id, self.contract.id)
        self.assertEqual(amendment.amendment_object, [BiomethaneContractAmendment.OTHER])
        self.assertEqual(amendment.signature_date, date.today())
        self.assertEqual(amendment.effective_date, date.today())
        self.assertEqual(amendment.amendment_details, "Modification spécifique non listée")

    def test_amendment_add_serializer_missing_required_fields(self):
        """Test validation errors for missing required fields"""
        data = {
            # Missing: signature_date, effective_date, amendment_object, amendment_file
        }

        context = {"entity": self.producer_entity}
        serializer = BiomethaneContractAmendmentAddSerializer(data=data, context=context)

        self.assertFalse(serializer.is_valid())
        self.assertIn("signature_date", serializer.errors)
        self.assertIn("effective_date", serializer.errors)
        self.assertIn("amendment_object", serializer.errors)
        self.assertIn("amendment_file", serializer.errors)

    def test_amendment_add_serializer_invalid_amendment_object(self):
        """Test validation error for invalid amendment object"""
        test_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")

        data = {
            "signature_date": date.today().isoformat(),
            "effective_date": date.today().isoformat(),
            "amendment_object": ["INVALID_CHOICE"],
            "amendment_file": test_file,
        }

        context = {"entity": self.producer_entity}
        serializer = BiomethaneContractAmendmentAddSerializer(data=data, context=context)

        self.assertFalse(serializer.is_valid())
        self.assertIn("amendment_object", serializer.errors)

    def test_amendment_add_serializer_multiple_amendment_objects(self):
        """Test creating amendment with multiple amendment objects"""
        test_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")

        data = {
            "signature_date": date.today().isoformat(),
            "effective_date": date.today().isoformat(),
            "amendment_object": [
                BiomethaneContractAmendment.CMAX_PAP_UPDATE,
                BiomethaneContractAmendment.INPUT_BONUS_UPDATE,
            ],
            "amendment_file": test_file,
        }

        context = {"entity": self.producer_entity}
        serializer = BiomethaneContractAmendmentAddSerializer(data=data, context=context)

        self.assertTrue(serializer.is_valid())
        amendment = serializer.save()

        self.assertEqual(amendment.contract_id, self.contract.id)
        self.assertEqual(len(amendment.amendment_object), 2)
        self.assertIn(BiomethaneContractAmendment.CMAX_PAP_UPDATE, amendment.amendment_object)
        self.assertIn(BiomethaneContractAmendment.INPUT_BONUS_UPDATE, amendment.amendment_object)

    def test_amendment_add_serializer_other_requires_details(self):
        """Test validation that amendment_details is required when amendment_object contains OTHER"""
        test_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")

        data = {
            "signature_date": date.today().isoformat(),
            "effective_date": date.today().isoformat(),
            "amendment_object": [BiomethaneContractAmendment.OTHER],
            "amendment_file": test_file,
            # Missing amendment_details
        }

        context = {"entity": self.producer_entity}
        serializer = BiomethaneContractAmendmentAddSerializer(data=data, context=context)

        self.assertFalse(serializer.is_valid())
        self.assertIn("amendment_details", serializer.errors)
