from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneProductionUnit
from biomethane.views.production_unit import BiomethaneProductionUnitViewSet
from core.models import Entity
from core.tests_utils import setup_current_user


class BiomethaneProductionUnitViewsTests(TestCase):
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

    @patch("biomethane.views.production_unit.production_unit.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that the write actions are correctly defined"""
        viewset = BiomethaneProductionUnitViewSet()
        viewset.action = "retrieve"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with(["upsert"], "retrieve")

    def test_put_upsert_creates_production_unit(self):
        """Test that PUT creates a production unit when it doesn't exist."""
        upsert_data = {
            "unit_name": "Upsert Unit",
            "siret_number": "11111111111111",
            "company_address": "100 Upsert Street",
            "unit_type": "AGRICULTURAL_AUTONOMOUS",
        }

        # First PUT should create the production unit (201)
        response = self.client.put(self.production_unit_url, upsert_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify it was created in database
        production_unit = BiomethaneProductionUnit.objects.get(producer=self.producer_entity)
        self.assertEqual(production_unit.unit_name, "Upsert Unit")

        # Verify only one production unit exists
        self.assertEqual(BiomethaneProductionUnit.objects.filter(producer=self.producer_entity).count(), 1)

    def test_put_upsert_updates_existing_production_unit(self):
        """Test that PUT updates an existing production unit."""
        # Create initial production unit
        upsert_data = {
            "unit_name": "Upsert Unit",
            "siret_number": "11111111111111",
            "company_address": "100 Upsert Street",
            "unit_type": "AGRICULTURAL_AUTONOMOUS",
        }

        response = self.client.put(self.production_unit_url, upsert_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update the production unit
        updated_data = upsert_data.copy()
        updated_data["unit_name"] = "Updated Upsert Unit"
        updated_data["production_efficiency"] = 90.5

        response = self.client.put(self.production_unit_url, updated_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify it was updated in database
        production_unit = BiomethaneProductionUnit.objects.get(producer=self.producer_entity)
        self.assertEqual(production_unit.unit_name, "Updated Upsert Unit")
        self.assertEqual(production_unit.production_efficiency, 90.5)

        # Verify only one production unit exists
        self.assertEqual(BiomethaneProductionUnit.objects.filter(producer=self.producer_entity).count(), 1)
