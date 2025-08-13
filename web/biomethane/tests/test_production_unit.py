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

    def test_basic_crud_works(self):
        # POST creates production unit
        data = {
            "unit_name": "Test Unit",
            "siret_number": "12345678901234",
            "company_address": "123 Test Street",
            "unit_type": "AGRICULTURAL_AUTONOMOUS",
            "sanitary_approval_number": "SA12345",
            "hygienization_exemption_type": "TOTAL",
            "icpe_number": "ICPE12345",
            "icpe_regime": "AUTHORIZATION",
            "process_type": "LIQUID_PROCESS",
            "methanization_process": "CONTINUOUS_INFINITELY_MIXED",
            "production_efficiency": 85.0,
            "installed_meters": [
                BiomethaneProductionUnit.BIOGAS_PRODUCTION_FLOWMETER,
                BiomethaneProductionUnit.GLOBAL_ELECTRICAL_METER,
            ],
            "raw_digestate_treatment_steps": "No additional steps",
            "liquid_phase_treatment_steps": "Standard treatment",
            "solid_phase_treatment_steps": "Composting",
            "digestate_valorization_methods": [BiomethaneProductionUnit.SPREADING],
            "spreading_management_methods": [BiomethaneProductionUnit.DIRECT_SPREADING],
            "digestate_sale_type": "DIG_AGRI_SPECIFICATIONS",
        }

        response = self.client.post(self.production_unit_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(BiomethaneProductionUnit.objects.filter(producer=self.producer_entity).exists())

        # GET retrieves it back correctly
        response = self.client.get(self.production_unit_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unit_name"], "Test Unit")
        self.assertEqual(response.data["producer"], self.producer_entity.id)

        # PATCH updates fields properly
        update_data = {"unit_name": "Updated Unit"}
        response = self.client.patch(self.production_unit_url, update_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unit_name"], "Updated Unit")

    def test_entity_constraint(self):
        # Create first production unit
        BiomethaneProductionUnit.objects.create(
            producer=self.producer_entity,
            unit_name="First Unit",
            siret_number="12345678901234",
            company_address="456 First Street",
            unit_type="AGRICULTURAL_AUTONOMOUS",
            sanitary_approval_number="SA56789",
            hygienization_exemption_type="PARTIAL",
            icpe_number="ICPE56789",
            icpe_regime="AUTHORIZATION",
            process_type="LIQUID_PROCESS",
            methanization_process="CONTINUOUS_INFINITELY_MIXED",
            production_efficiency=85.0,
            installed_meters=[
                BiomethaneProductionUnit.PURIFICATION_FLOWMETER,
            ],
            raw_digestate_treatment_steps="Basic steps",
            liquid_phase_treatment_steps="Filtration",
            solid_phase_treatment_steps="Drying",
            digestate_valorization_methods=[BiomethaneProductionUnit.SPREADING],
            spreading_management_methods=[BiomethaneProductionUnit.SPREADING_VIA_PROVIDER],
            digestate_sale_type="HOMOLOGATION",
        )

        # Try to create second production unit for same entity
        data = {
            "unit_name": "Second Unit",
            "siret_number": "98765432109876",
            "company_address": "789 Second Street",
            "unit_type": "AGRICULTURAL_TERRITORIAL",
            "sanitary_approval_number": "SA98765",
            "hygienization_exemption_type": "TOTAL",
            "icpe_number": "ICPE98765",
            "icpe_regime": "REGISTRATION",
            "process_type": "DRY_PROCESS",
            "methanization_process": "PLUG_FLOW_SEMI_CONTINUOUS",
            "production_efficiency": 75.0,
            "installed_meters": [
                BiomethaneProductionUnit.FLARING_FLOWMETER,
                BiomethaneProductionUnit.HEATING_FLOWMETER,
            ],
            "raw_digestate_treatment_steps": "Advanced steps",
            "liquid_phase_treatment_steps": "Membrane treatment",
            "solid_phase_treatment_steps": "Pelletizing",
            "digestate_valorization_methods": [BiomethaneProductionUnit.COMPOSTING],
            "spreading_management_methods": [BiomethaneProductionUnit.SALE],
            "digestate_sale_type": "STANDARDIZED_PRODUCT",
        }

        response = self.client.post(self.production_unit_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("producer", response.data)

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
        from biomethane.serializers.production_unit import BiomethaneProductionUnitAddSerializer

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
        serializer = BiomethaneProductionUnitAddSerializer(data=valid_data)
        # Should validate successfully for valid choices
        self.assertTrue(serializer.is_valid())

        # Test invalid installed_meters
        invalid_data = valid_data.copy()
        invalid_data["installed_meters"] = ["INVALID_METER_TYPE"]
        serializer = BiomethaneProductionUnitAddSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("installed_meters", serializer.errors)

        # Test invalid digestate valorization methods
        invalid_data = valid_data.copy()
        invalid_data["digestate_valorization_methods"] = ["INVALID_VALORIZATION_METHOD"]
        serializer = BiomethaneProductionUnitAddSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("digestate_valorization_methods", serializer.errors)

        # Test invalid spreading management methods
        invalid_data = valid_data.copy()
        invalid_data["spreading_management_methods"] = ["INVALID_SPREADING_METHOD"]
        serializer = BiomethaneProductionUnitAddSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("spreading_management_methods", serializer.errors)
