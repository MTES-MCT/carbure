from api.v4.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse


class UserTest(TestCase):
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

    def test_get_settings(self):
        response = self.client.get(reverse("user"))
        # api works
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("rights", data)
        self.assertIn("email", data)
        self.assertIn("requests", data)
