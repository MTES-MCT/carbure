import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, Pays, MatierePremiere, Biocarburant, Depot
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
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

    def test_mac_option(self):
        url = "api-v3-settings-rfc"

        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_mac": "true"})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url), {"has_mac": "true"})
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_mac": "true"})
        self.assertEqual(response.status_code, 403)
        # rights RW, mac option OK
        response = self.client.post(reverse(url), {"entity_id": self.entity2.id, "has_mac": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, True)
        # should pass
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_mac": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_mac, True)

        # disable:
        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_mac": "false"})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url), {"has_mac": "false"})
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_mac": "false"})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_mac": "false"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_mac, False)

        # revert
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_mac": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_mac, True)

    def test_trading_option(self):
        url = "api-v3-settings-trading"

        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_trading": "true"})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url), {"has_trading": "true"})
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_trading": "true"})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_trading": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, True)

        # disable:
        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_trading": "false"})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url), {"has_trading": "false"})
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_trading": "false"})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_trading": "false"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, False)

        # revert
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_trading": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, True)

        # should not work on Operator
        # because operators cannot trade # deprecated as of 2022
        # response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        # self.assertEqual(response.status_code, 400)

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

    def test_invites(self):
        # try invite/revoke as non-admin
        right = UserRights.objects.get(entity=self.entity1, user=self.user1)
        right.role = UserRights.RO
        right.save()

        url = "api-v3-settings-invite-user"
        response = self.client.post(
            reverse(url), {"entity_id": self.entity1.id, "email": self.user2.email, "role": UserRights.RO}
        )
        self.assertEqual(response.status_code, 403)
        url = "api-v3-settings-revoke-user"
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "email": self.user2.email})
        self.assertEqual(response.status_code, 403)

        UserRights.objects.filter(entity=self.entity1, user=self.user1).update(role=UserRights.ADMIN)
        # invite_nonexisting_user
        url = "api-v3-settings-invite-user"
        response = self.client.post(
            reverse(url), {"entity_id": self.entity1.id, "email": "totopouet@gmail.com", "role": UserRights.RO}
        )
        self.assertEqual(response.status_code, 400)
        # test_invite_ro
        url = "api-v3-settings-invite-user"
        response = self.client.post(
            reverse(url), {"entity_id": self.entity1.id, "email": self.user2.email, "role": UserRights.RO}
        )
        self.assertEqual(response.status_code, 200)
        right = UserRights.objects.get(entity=self.entity1, user=self.user2)
        self.assertEqual(right.role, UserRights.RO)
        # test_invite_rw
        response = self.client.post(
            reverse(url), {"entity_id": self.entity1.id, "email": self.user2.email, "role": UserRights.RW}
        )
        self.assertEqual(response.status_code, 200)
        right = UserRights.objects.get(entity=self.entity1, user=self.user2)
        self.assertEqual(right.role, UserRights.RW)
        # test_invite_admin
        response = self.client.post(
            reverse(url), {"entity_id": self.entity1.id, "email": self.user2.email, "role": UserRights.ADMIN}
        )
        self.assertEqual(response.status_code, 200)
        right = UserRights.objects.get(entity=self.entity1, user=self.user2)
        self.assertEqual(right.role, UserRights.ADMIN)
        # test_invite_auditor (without expiration date)
        response = self.client.post(
            reverse(url), {"entity_id": self.entity1.id, "email": self.user2.email, "role": UserRights.AUDITOR}
        )
        self.assertEqual(response.status_code, 400)
        # test_invite_auditor (with expiration date)
        response = self.client.post(
            reverse(url),
            {
                "entity_id": self.entity1.id,
                "email": self.user2.email,
                "role": UserRights.AUDITOR,
                "expiration_date": "2021-12-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        right = UserRights.objects.get(entity=self.entity1, user=self.user2)
        self.assertEqual(right.role, UserRights.AUDITOR)
        # test_invite_unknown_role
        response = self.client.post(
            reverse(url), {"entity_id": self.entity1.id, "email": self.user2.email, "role": "tougoudou"}
        )
        self.assertEqual(response.status_code, 400)

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
