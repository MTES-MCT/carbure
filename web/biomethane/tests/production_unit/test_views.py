from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories.production_unit import BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneProductionUnit
from core.models import Department, Entity, ExternalAdminRights
from core.tests_utils import setup_current_user
from entity.models import EntityScope


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

    def test_put_upsert_creates_production_unit(self):
        """Test that PUT creates a production unit when it doesn't exist."""
        upsert_data = {
            "name": "Upsert Unit",
            "site_siret": "11111111111111",
            "address": "100 Upsert Street",
            "unit_type": "AGRICULTURAL_AUTONOMOUS",
        }

        # First PUT should create the production unit (201)
        response = self.client.put(self.production_unit_url, upsert_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify it was created in database
        production_unit = BiomethaneProductionUnit.objects.get(producer=self.producer_entity)
        self.assertEqual(production_unit.name, "Upsert Unit")

        # Verify only one production unit exists
        self.assertEqual(BiomethaneProductionUnit.objects.filter(producer=self.producer_entity).count(), 1)

    def test_put_upsert_updates_existing_production_unit(self):
        """Test that PUT updates an existing production unit."""
        # Create initial production unit
        upsert_data = {
            "name": "Upsert Unit",
            "site_siret": "11111111111111",
            "address": "100 Upsert Street",
            "unit_type": "AGRICULTURAL_AUTONOMOUS",
        }

        response = self.client.put(self.production_unit_url, upsert_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update the production unit
        updated_data = upsert_data.copy()
        updated_data["name"] = "Updated Upsert Unit"
        updated_data["production_efficiency"] = 90.5

        response = self.client.put(self.production_unit_url, updated_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify it was updated in database
        production_unit = BiomethaneProductionUnit.objects.get(producer=self.producer_entity)
        self.assertEqual(production_unit.name, "Updated Upsert Unit")
        self.assertEqual(production_unit.production_efficiency, 90.5)

        # Verify only one production unit exists
        self.assertEqual(BiomethaneProductionUnit.objects.filter(producer=self.producer_entity).count(), 1)

    def test_retrieve_production_unit_error_with_producer_using_producer_id_param(self):
        """Test that a producer cannot use producer_id param to access another producer's data (IDOR protection)."""
        producer_entity_2 = Entity.objects.create(
            name="Test Producer 2",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        url = reverse("biomethane-production-unit")
        params = {"entity_id": self.producer_entity.id, "producer_id": producer_entity_2.id}
        response = self.client.get(url, params)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_production_unit_with_dreal_and_producer_id(self):
        """Test DREAL can access production unit filtered by producer_id."""
        department = Department.objects.create(code_dept="69", name="Rhône")
        production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity, department=department)

        dreal = Entity.objects.create(name="Test DREAL", entity_type=Entity.EXTERNAL_ADMIN)
        ExternalAdminRights.objects.create(entity=dreal, right=ExternalAdminRights.DREAL)
        EntityScope.objects.create(
            entity=dreal,
            content_type=ContentType.objects.get_for_model(Department),
            object_id=department.id,
        )

        setup_current_user(self, "dreal@carbure.local", "DREAL", "gogogo", [(dreal, "ADMIN")])

        url = reverse("biomethane-production-unit")
        params = {"entity_id": dreal.id, "producer_id": self.producer_entity.id}
        response = self.client.get(url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], production_unit.id)
