import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import MatierePremiere, Biocarburant, Pays, Entity, ProductionSite, Depot
from api.v3.common.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice


class CommonAPITest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        # let's create a user
        self.password = "totopouet"
        self.user1 = user_model.objects.create_user(
            email="testuser1@toto.com", name="Le Super Testeur 1", password=self.password
        )
        loggedin = self.client.login(username=self.user1.email, password=self.password)
        self.assertTrue(loggedin)
        # pass otp verification
        response = self.client.post(reverse("auth-request-otp"))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse("auth-verify-otp"), {"otp_token": device.token})
        self.assertEqual(response.status_code, 200)

    def test_create_delivery_site(self):
        # check how many sites exist
        urlget = "resources-depots"
        urlpost = "api-v3-public-create-delivery-site"
        response = self.client.get(reverse(urlget))
        # api works
        self.assertEqual(response.status_code, 200)
        prev_len = len(response.json()["data"])

        # create a new one
        usa, _ = Pays.objects.update_or_create(name="USA", code_pays="US")
        response = self.client.post(
            reverse(urlpost),
            {
                "name": "Hangar 18",
                "city": "Roswell",
                "country_code": usa.code_pays,
                "depot_id": "US666",
                "depot_type": "EFS",
                "address": "Route 66",
                "postal_code": "91210",
            },
        )
        # api works
        self.assertEqual(response.status_code, 200)

        # check that we have one more than before
        response = self.client.get(reverse(urlget))
        self.assertEqual(prev_len + 1, len(response.json()["data"]))
