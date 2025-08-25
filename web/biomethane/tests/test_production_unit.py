from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneProductionUnit
from core.models import Entity
from core.tests_utils import setup_current_user


class BiomethaneProductionUnitViewSetTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.producer_entity, "RW")],
        )

        self.production_unit_url = reverse("biomethane-production-unit")
        self.production_unit_url += "?entity_id=" + str(self.producer_entity.id)

    def test_permission_boundary(self):
        # Create non-biomethane producer entity
        wrong_entity = Entity.objects.create(
            name="Wrong Entity",
            entity_type=Entity.OPERATOR,
        )

        setup_current_user(
            self,
            "wrong@carbure.local",
            "Wrong User",
            "gogogo2",
            [(wrong_entity, "RW")],
        )

        wrong_url = reverse("biomethane-production-unit")
        wrong_url += "?entity_id=" + str(wrong_entity.id)

        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_json_field_validation(self):
        """Test validation of the new JSON fields using Django REST Framework ListField."""
        from biomethane.serializers.production_unit import BiomethaneProductionUnitUpsertSerializer

        # Test valid data
        valid_data = {
            "unit_name": "Test Unit",
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

        # Test invalid installed_meters
        invalid_data = valid_data.copy()
        invalid_data["installed_meters"] = ["INVALID_METER_TYPE"]
        serializer = BiomethaneProductionUnitUpsertSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("installed_meters", serializer.errors)

        # Test invalid digestate valorization methods
        invalid_data = valid_data.copy()
        invalid_data["digestate_valorization_methods"] = ["INVALID_VALORIZATION_METHOD"]
        serializer = BiomethaneProductionUnitUpsertSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("digestate_valorization_methods", serializer.errors)

        # Test invalid spreading management methods
        invalid_data = valid_data.copy()
        invalid_data["spreading_management_methods"] = ["INVALID_SPREADING_METHOD"]
        serializer = BiomethaneProductionUnitUpsertSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("spreading_management_methods", serializer.errors)

    def test_put_upsert_functionality(self):
        """Test that PUT creates or updates production unit automatically."""
        upsert_data = {
            "unit_name": "Upsert Unit",
            "siret_number": "11111111111111",
            "company_address": "100 Upsert Street",
            "unit_type": "AGRICULTURAL_AUTONOMOUS",
        }

        # First PUT should create the production unit (201)
        response = self.client.put(self.production_unit_url, upsert_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["unit_name"], "Upsert Unit")

        # Verify it was created in database
        production_unit = BiomethaneProductionUnit.objects.get(producer=self.producer_entity)
        self.assertEqual(production_unit.unit_name, "Upsert Unit")

        # Second PUT should update the existing production unit (200)
        updated_data = upsert_data.copy()
        updated_data["unit_name"] = "Updated Upsert Unit"
        updated_data["production_efficiency"] = 90.5

        response = self.client.put(self.production_unit_url, updated_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unit_name"], "Updated Upsert Unit")
        self.assertEqual(float(response.data["production_efficiency"]), 90.5)

        # Verify it was updated in database
        production_unit.refresh_from_db()
        self.assertEqual(production_unit.unit_name, "Updated Upsert Unit")
        self.assertEqual(production_unit.production_efficiency, 90.5)

        # Verify only one production unit exists
        self.assertEqual(BiomethaneProductionUnit.objects.filter(producer=self.producer_entity).count(), 1)
