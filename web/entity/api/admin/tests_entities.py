from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse


class AdminEntitiesTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)

    def test_get_entities(self):
        response = self.client.get(reverse("transactions-admin-entities"), {"entity_id": self.admin.id})
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns at least 5 entities
        self.assertGreaterEqual(len(response.json()["data"]), 5)

        # check if querying works
        response = self.client.get(reverse("transactions-admin-entities"), {"q": "prod", "entity_id": self.admin.id})
        # works
        self.assertEqual(response.status_code, 200)
        # and returns at least 2 entities
        data = response.json()["data"]
        self.assertGreaterEqual(len(data), 2)
        # check if the content is correct
        random_entity = data[0]["entity"]
        self.assertIn("entity_type", random_entity)
        self.assertIn("name", random_entity)

    def test_get_entities_details(self):
        response = self.client.get(
            reverse("transactions-admin-entities-details"),
            {"entity_id": self.admin.id, "company_id": self.admin.id},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["name"], "MTE - DGEC")
