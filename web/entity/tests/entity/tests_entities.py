from django.test import TestCase
from django.urls import reverse

from biomethane.models import BiomethaneProductionUnit
from core.models import Entity
from core.tests_utils import setup_current_user
from entity.factories.entity import EntityFactory


class AdminEntitiesTest(TestCase):
    def setUp(self):
        self.entity1 = EntityFactory.create(name="Entity operator", entity_type=Entity.OPERATOR)
        self.admin = EntityFactory.create(name="Entity admin", entity_type=Entity.ADMIN)
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)

    def test_get_entities_details(self):
        response = self.client.get(
            reverse("entity-detail", kwargs={"id": self.admin.id}) + f"?entity_id={self.admin.id}",
            {"entity_id": self.admin.id, "company_id": self.admin.id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == self.admin.name

    def test_create_entity_success(self):
        data = {"name": "Test Entity", "entity_type": "Producteur", "has_saf": True, "has_elec": False}

        response = self.client.post(reverse("entity-list") + f"?entity_id={self.admin.id}", data)

        assert response.status_code == 201
        assert Entity.objects.filter(name="Test Entity").exists()
        assert not BiomethaneProductionUnit.objects.filter(producer__name="Test Entity").exists()

    def test_create_biomethane_producer_creates_production_unit(self):
        data = {
            "name": "Biomethane producer",
            "entity_type": Entity.BIOMETHANE_PRODUCER,
            "has_saf": False,
            "has_elec": False,
            "company_address": "1 rue de la Méthanisation",
            "postal_code": "75001",
            "city": "Paris",
            "insee_code": "75101",
            "site_siret": "12345678901234",
        }

        response = self.client.post(reverse("entity-list") + f"?entity_id={self.admin.id}", data)

        assert response.status_code == 201
        producer = Entity.objects.get(name=data["name"])
        production_unit = BiomethaneProductionUnit.objects.get(producer=producer)
        assert production_unit.address == data["company_address"]
        assert production_unit.site_siret == data["site_siret"]

    def test_create_biomass_operator(self):
        data = {
            "name": "Biomass operator",
            "entity_type": Entity.SOLID_BIOMASS_ENERGY_PRODUCER,
            "has_saf": False,
            "has_elec": False,
        }

        response = self.client.post(reverse("entity-list") + f"?entity_id={self.admin.id}", data)

        assert response.status_code == 201
        assert Entity.objects.filter(name=data["name"], entity_type=Entity.SOLID_BIOMASS_ENERGY_PRODUCER).exists()

    def test_create_entity_duplicate_name(self):
        Entity.objects.create(name="Duplicate Entity", entity_type="Producteur")

        data = {"name": "Duplicate Entity", "entity_type": "Producteur", "has_saf": True, "has_elec": False}

        response = self.client.post(reverse("entity-list") + f"?entity_id={self.admin.id}", data)

        assert response.status_code == 400
        assert "name" in response.data
