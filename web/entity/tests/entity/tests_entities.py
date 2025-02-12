from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user


class AdminEntitiesTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)

    def test_get_entities(self):
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}", {"entity_id": self.admin.id})
        # api works
        assert response.status_code == 200
        # and returns at least 5 entities
        assert len(response.json()) >= 5

        # check if querying works
        response = self.client.get(
            reverse("entity-list") + f"?entity_id={self.admin.id}", {"q": "prod", "entity_id": self.admin.id}
        )
        # works
        assert response.status_code == 200
        # and returns at least 2 entities
        data = response.json()
        assert len(data) >= 2
        # check if the content is correct
        random_entity = data[0]["entity"]
        assert "entity_type" in random_entity
        assert "name" in random_entity

    def test_get_entities_details(self):
        response = self.client.get(
            reverse("entity-detail", kwargs={"id": self.admin.id}) + f"?entity_id={self.admin.id}",
            {"entity_id": self.admin.id, "company_id": self.admin.id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MTE - DGEC"

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
