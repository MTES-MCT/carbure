from django.test import TestCase

from biomethane.models import BiomethaneProductionUnit
from biomethane.serializers.production_unit import BiomethaneProductionUnitUpsertSerializer
from core.models import Entity


class BiomethaneProductionUnitSerializerTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_json_field_validation_with_valid_data(self):
        """Test validation of JSON fields with valid choices."""
        valid_data = {
            "name": "Test Unit",
            "installed_meters": [
                BiomethaneProductionUnit.BIOGAS_PRODUCTION_FLOWMETER,
                BiomethaneProductionUnit.GLOBAL_ELECTRICAL_METER,
            ],
            "digestate_valorization_methods": [BiomethaneProductionUnit.SPREADING],
            "spreading_management_methods": [BiomethaneProductionUnit.DIRECT_SPREADING],
        }
        serializer = BiomethaneProductionUnitUpsertSerializer(data=valid_data, context={"entity": self.producer_entity})

        # Should validate successfully for valid choices
        self.assertTrue(serializer.is_valid())

    def test_json_field_validation_invalid_installed_meters(self):
        """Test validation rejects invalid installed_meters."""
        invalid_data = {
            "name": "Test Unit",
            "installed_meters": ["INVALID_METER_TYPE"],
            "digestate_valorization_methods": [BiomethaneProductionUnit.SPREADING],
            "spreading_management_methods": [BiomethaneProductionUnit.DIRECT_SPREADING],
        }
        serializer = BiomethaneProductionUnitUpsertSerializer(data=invalid_data, context={"entity": self.producer_entity})

        self.assertFalse(serializer.is_valid())
        self.assertIn("installed_meters", serializer.errors)

    def test_json_field_validation_invalid_digestate_valorization_methods(self):
        """Test validation rejects invalid digestate valorization methods."""
        invalid_data = {
            "name": "Test Unit",
            "installed_meters": [BiomethaneProductionUnit.BIOGAS_PRODUCTION_FLOWMETER],
            "digestate_valorization_methods": ["INVALID_VALORIZATION_METHOD"],
            "spreading_management_methods": [BiomethaneProductionUnit.DIRECT_SPREADING],
        }
        serializer = BiomethaneProductionUnitUpsertSerializer(data=invalid_data, context={"entity": self.producer_entity})

        self.assertFalse(serializer.is_valid())
        self.assertIn("digestate_valorization_methods", serializer.errors)

    def test_json_field_validation_invalid_spreading_management_methods(self):
        """Test validation rejects invalid spreading management methods."""
        invalid_data = {
            "name": "Test Unit",
            "installed_meters": [BiomethaneProductionUnit.BIOGAS_PRODUCTION_FLOWMETER],
            "digestate_valorization_methods": [BiomethaneProductionUnit.SPREADING],
            "spreading_management_methods": ["INVALID_SPREADING_METHOD"],
        }
        serializer = BiomethaneProductionUnitUpsertSerializer(data=invalid_data, context={"entity": self.producer_entity})

        self.assertFalse(serializer.is_valid())
        self.assertIn("spreading_management_methods", serializer.errors)
