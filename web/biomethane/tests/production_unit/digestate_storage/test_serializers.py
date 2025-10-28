from django.test import TestCase

from biomethane.serializers.production_unit.digestate_storage import BiomethaneDigestateStorageInputSerializer
from core.models import Entity


class BiomethaneDigestateStorageSerializerTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_digestate_storage_input_serializer_valid_data(self):
        """Test creating digestate storage with valid data."""
        data = {
            "type": "LAGOON",
            "capacity": 5000.0,
            "has_cover": True,
            "has_biogas_recovery": True,
        }

        serializer = BiomethaneDigestateStorageInputSerializer(data=data, context={"entity": self.producer_entity})
        self.assertTrue(serializer.is_valid())

        # Create the storage
        storage = serializer.save()
        self.assertEqual(storage.producer, self.producer_entity)
        self.assertEqual(storage.type, "LAGOON")
        self.assertEqual(storage.capacity, 5000.0)
        self.assertTrue(storage.has_cover)
        self.assertTrue(storage.has_biogas_recovery)

    def test_digestate_storage_input_serializer_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        data = {
            "type": "LAGOON",
            # Missing capacity
        }

        serializer = BiomethaneDigestateStorageInputSerializer(data=data, context={"entity": self.producer_entity})
        self.assertFalse(serializer.is_valid())
        self.assertIn("capacity", serializer.errors)
