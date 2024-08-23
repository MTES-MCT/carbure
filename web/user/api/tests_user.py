from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Entity, UserRights
from core.tests_utils import setup_current_user


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
            self,
            "admin@carbure.local",
            "Tester",
            "gogogo",
            [(self.admin, "RW")],
            is_staff=True,
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
        producer, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        # admin
        User = get_user_model()
        user_admin = User.objects.create_user(email="tester@carbure.local", name="Requestor", password="gogogo")
        UserRights.objects.update_or_create(user=user_admin, entity=producer, defaults={"role": UserRights.ADMIN})

        # requester
        setup_current_user(self, "tester-requesting@carbure.local", "Tester", "gogogo", [])

        # get settings - 0 pending requests
        url = "user"
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("requests", data)
        prev_len = len(data["requests"])

        # request access
        postdata = {"entity_id": producer.id, "comment": "", "role": "RO"}
        response = self.client.post(reverse("user-request-access"), postdata)
        self.assertEqual(response.status_code, 200)

        # get settings - 1 pending request
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        new_len = len(data["requests"])
        self.assertEqual(prev_len + 1, new_len)
