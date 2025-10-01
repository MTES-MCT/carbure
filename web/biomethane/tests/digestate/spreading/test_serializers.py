from django.test import TestCase
from rest_framework import serializers

from biomethane.serializers.digestate.spreading import BiomethaneDigestateSpreadingAddSerializer


class BiomethaneDigestateSpreadingAddSerializerTests(TestCase):
    def test_input_validation_success(self):
        """Test serializer creation with required fields"""
        valid_data = {
            "spreading_department": "75",
            "spread_quantity": 100.0,
            "spread_parcels_area": 50.0,
        }

        serializer = BiomethaneDigestateSpreadingAddSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_input_validation_missing_required_fields(self):
        """Test serializer validation with missing required fields."""
        incomplete_data = {
            # Missing spreading_department, spread_quantity, spread_parcels_area
        }

        serializer = BiomethaneDigestateSpreadingAddSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())

        # Check that required fields are in errors
        required_fields = ["spreading_department", "spread_quantity", "spread_parcels_area"]
        for field in required_fields:
            self.assertIn(field, serializer.errors)

    def test_create_digestate_not_found(self):
        """Test serializer creation when digestate is not found in context."""
        valid_data = {
            "spreading_department": "75",
            "spread_quantity": 100.0,
            "spread_parcels_area": 50.0,
        }

        serializer = BiomethaneDigestateSpreadingAddSerializer(data=valid_data, context={"entity": None, "year": 2024})
        self.assertTrue(serializer.is_valid())

        with self.assertRaises(serializers.ValidationError) as context_manager:
            serializer.save()

        error = context_manager.exception
        self.assertIn("year", error.detail)
