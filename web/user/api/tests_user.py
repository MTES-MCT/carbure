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
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], is_staff=True
        )

    def test_get_settings(self):
        response = self.client.get(reverse("user"))
        # api works
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("rights", data)
        self.assertIn("email", data)
        self.assertIn("requests", data)

    def test_entity_access_request(self):
        # get settings - 0 pending requests
        url = "user"
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("requests", data)
        prev_len = len(data["requests"])

        e, _ = Entity.objects.update_or_create(name="Entity test", entity_type="Producteur")
        postdata = {"entity_id": e.id, "comment": "", "role": "RO"}
        response = self.client.post(reverse("user-request-access"), postdata)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        new_len = len(data["requests"])
        self.assertEqual(prev_len + 1, new_len)
