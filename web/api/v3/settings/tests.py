from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, Pays
from django_otp.plugins.otp_email.models import EmailDevice


class SettingsAPITest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user_email = "testuser1@toto.com"
        self.user_password = "totopouet"
        self.user1 = user_model.objects.create_user(
            email=self.user_email, name="Le Super Testeur 1", password=self.user_password
        )
        self.user2 = user_model.objects.create_user(
            email="testuser2@toto.com", name="Le Super Testeur 2", password=self.user_password
        )

        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        self.entity2, _ = Entity.objects.update_or_create(name="Le Super Operateur 1", entity_type="Opérateur")
        self.entity3, _ = Entity.objects.update_or_create(name="Le Super Trader 1", entity_type="Trader")

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1, defaults={"role": UserRights.ADMIN})
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2, defaults={"role": UserRights.RW})

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)
        # pass otp verification
        response = self.client.post(reverse("auth-request-otp"))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse("auth-verify-otp"), {"otp_token": device.token})
        self.assertEqual(response.status_code, 200)

        # some data
        fr, _ = Pays.objects.get_or_create(code_pays="FR", name="France")

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

    def test_add_production_site(self):
        postdata = {"entity_id": self.entity2.id}
        url = "entity-production-sites-add"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_COUNTRY_CODE")
        postdata["country_code"] = "ZZ"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_NAME")
        postdata["name"] = "Site de production 007"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_COM_DATE")
        postdata["date_mise_en_service"] = "12/05/2007"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_GHG_OPTION")
        postdata["ges_option"] = "DEFAULT"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_ID")
        postdata["site_id"] = "FR78895468"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_ZIP_CODE")
        postdata["postal_code"] = "64430"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_NAME")
        postdata["manager_name"] = "William Rock"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_PHONE")
        postdata["manager_phone"] = "0145247000"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_EMAIL")
        postdata["manager_email"] = "will.rock@example.com"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_CITY")
        postdata["city"] = "Guermiette"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_COM_DATE_WRONG_FORMAT")
        postdata["date_mise_en_service"] = "2007-05-12"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_COUNTRY_CODE")
        postdata["country_code"] = "FR"
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_PRODUCER")
        postdata["entity_id"] = self.entity1.id
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 200)
