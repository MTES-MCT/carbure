from django.test import TestCase
from django.urls import reverse

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

    def test_create_entity_duplicate_name(self):
        Entity.objects.create(name="Duplicate Entity", entity_type="Producteur")

        data = {"name": "Duplicate Entity", "entity_type": "Producteur", "has_saf": True, "has_elec": False}

        response = self.client.post(reverse("entity-list") + f"?entity_id={self.admin.id}", data)

        assert response.status_code == 400
        assert "name" in response.data
