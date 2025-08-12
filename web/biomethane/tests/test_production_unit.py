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
            "unit_type": BiomethaneProductionUnit.AGRICULTURAL_AUTONOMOUS,
            "sanitary_approval_number": "SA12345",
            "hygienization_exemption_type": BiomethaneProductionUnit.TOTAL,
            "icpe_number": "ICPE12345",
            "icpe_regime": BiomethaneProductionUnit.AUTHORIZATION,
            "process_type": BiomethaneProductionUnit.LIQUID_PROCESS,
            "methanization_process": BiomethaneProductionUnit.CONTINUOUS_INFINITELY_MIXED,
            "production_efficiency": 85.0,
            "raw_digestate_treatment_steps": "No additional steps",
            "liquid_phase_treatment_steps": "Standard treatment",
            "solid_phase_treatment_steps": "Composting",
            "digestate_valorization_method": BiomethaneProductionUnit.SPREADING,
            "spreading_management": BiomethaneProductionUnit.DIRECT_SPREADING,
            "digestate_sale_type": BiomethaneProductionUnit.DIG_AGRI_SPECIFICATIONS,
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
            unit_type=BiomethaneProductionUnit.AGRICULTURAL_AUTONOMOUS,
            sanitary_approval_number="SA56789",
            hygienization_exemption_type=BiomethaneProductionUnit.PARTIAL,
            icpe_number="ICPE56789",
            icpe_regime=BiomethaneProductionUnit.AUTHORIZATION,
            process_type=BiomethaneProductionUnit.LIQUID_PROCESS,
            methanization_process=BiomethaneProductionUnit.CONTINUOUS_INFINITELY_MIXED,
            production_efficiency=85.0,
            raw_digestate_treatment_steps="Basic steps",
            liquid_phase_treatment_steps="Filtration",
            solid_phase_treatment_steps="Drying",
            digestate_valorization_method=BiomethaneProductionUnit.SPREADING,
            spreading_management=BiomethaneProductionUnit.SPREADING_VIA_PROVIDER,
            digestate_sale_type=BiomethaneProductionUnit.HOMOLOGATION,
        )

        # Try to create second production unit for same entity
        data = {
            "unit_name": "Second Unit",
            "siret_number": "98765432109876",
            "company_address": "789 Second Street",
            "unit_type": BiomethaneProductionUnit.AGRICULTURAL_TERRITORIAL,
            "sanitary_approval_number": "SA98765",
            "hygienization_exemption_type": BiomethaneProductionUnit.TOTAL,
            "icpe_number": "ICPE98765",
            "icpe_regime": BiomethaneProductionUnit.REGISTRATION,
            "process_type": BiomethaneProductionUnit.DRY_PROCESS,
            "methanization_process": BiomethaneProductionUnit.PLUG_FLOW_SEMI_CONTINUOUS,
            "production_efficiency": 75.0,
            "raw_digestate_treatment_steps": "Advanced steps",
            "liquid_phase_treatment_steps": "Membrane treatment",
            "solid_phase_treatment_steps": "Pelletizing",
            "digestate_valorization_method": BiomethaneProductionUnit.COMPOSTING,
            "spreading_management": BiomethaneProductionUnit.SALE,
            "digestate_sale_type": BiomethaneProductionUnit.STANDARDIZED_PRODUCT,
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
