from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_email.models import EmailDevice

from core.models import Entity, UserRights
from api.v3.admin.urls import urlpatterns


class AdminAPITest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_email = "superadmin@carbure.beta.gouv.fr"
        self.admin_password = "toto"
        self.fake_admin_email = "fakeadmin@carbure.beta.gouv.fr"
        self.fake_admin_password = "toto"

        self.admin_user = user_model.objects.create_user(
            email=self.admin_email, name="Super Admin", password=self.admin_password, is_staff=True
        )
        self.fake_admin_user = user_model.objects.create_user(
            email=self.fake_admin_email, name="Super Admin", password=self.fake_admin_password
        )

        # create OTP devices
        for user in [self.admin_user, self.fake_admin_user]:
            email_otp = EmailDevice()
            email_otp.user = user
            email_otp.name = "email"
            email_otp.confirmed = True
            email_otp.email = user.email
            email_otp.save()

        # let's create a few users
        self.user1 = user_model.objects.create_user(
            email="testuser1@toto.com", name="Le Super Testeur 1", password=self.fake_admin_password
        )
        self.user2 = user_model.objects.create_user(
            email="testuser2@toto.com", name="Le Super Testeur 2", password=self.fake_admin_password
        )
        self.user3 = user_model.objects.create_user(
            email="testuser3@toto.com", name="Testeur 3", password=self.fake_admin_password
        )

        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        self.entity2, _ = Entity.objects.update_or_create(name="Le Super Producteur 2", entity_type="Producteur")
        self.entity3, _ = Entity.objects.update_or_create(name="Le Super Administrateur 1", entity_type=Entity.ADMIN)
        self.entity4, _ = Entity.objects.update_or_create(name="Le Super Operateur 1", entity_type=Entity.OPERATOR)
        self.entity5, _ = Entity.objects.update_or_create(name="Le Super Trader 1", entity_type="Trader")

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity3)
        UserRights.objects.update_or_create(user=self.user2, entity=self.entity2)
        UserRights.objects.update_or_create(user=self.user3, entity=self.entity4)
        UserRights.objects.update_or_create(user=self.admin_user, entity=self.entity3)

        # login as an admin
        loggedin = self.client.login(username=self.admin_email, password=self.admin_password)
        self.assertTrue(loggedin)
        # pass otp
        usermodel = get_user_model()
        user = usermodel.objects.get(email=self.admin_email)
        response = self.client.post(reverse("api-v4-request-otp"))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=user)
        response = self.client.post(reverse("api-v4-verify-otp"), {"otp_token": device.token})
        self.assertEqual(response.status_code, 200)

    def test_accessrights_as_admin(self):
        for url in urlpatterns:
            response = self.client.get(reverse(url.name), {"entity_id": self.entity3.id})
            self.assertNotEqual(response.status_code, 403)

    def test_accessrights(self):
        loggedin = self.client.login(username=self.fake_admin_email, password=self.fake_admin_password)
        self.assertTrue(loggedin)
        # pass otp
        usermodel = get_user_model()
        user = usermodel.objects.get(email=self.fake_admin_email)
        response = self.client.post(reverse("api-v4-request-otp"))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=user)
        response = self.client.post(reverse("api-v4-verify-otp"), {"otp_token": device.token})
        self.assertEqual(response.status_code, 200)
        for url in urlpatterns:
            response = self.client.get(reverse(url.name), {"entity_id": self.entity3.id})
            self.assertEqual(response.status_code, 403)

    def test_create_entity(self):
        response = self.client.post(
            reverse("api-v3-admin-add-entity"),
            {"entity_id": self.entity3.id, "name": "Société Test", "category": "Producteur"},
        )
        self.assertEquals(response.status_code, 200)
        # check if entity has been created actually exists
        response = self.client.get(reverse("admin-entities"), {"q": "Test", "entity_id": self.entity3.id})
        self.assertEqual(response.status_code, 200)
        # and returns 1 entity
        jc = response.json()["data"][0]["entity"]
        self.assertEqual(jc["name"], "Société Test")
        self.assertEqual(jc["entity_type"], "Producteur")

        # make sure all categories are supported
        response = self.client.post(
            reverse("api-v3-admin-add-entity"),
            {"entity_id": self.entity3.id, "name": "Opérateur Test", "category": Entity.OPERATOR},
        )
        obj = Entity.objects.get(name="Opérateur Test")
        self.assertEquals(obj.entity_type, Entity.OPERATOR)
        response = self.client.post(
            reverse("api-v3-admin-add-entity"),
            {"entity_id": self.entity3.id, "name": "Trader Test", "category": "Trader"},
        )
        obj = Entity.objects.get(name="Trader Test")
        self.assertEquals(obj.entity_type, "Trader")
        response = self.client.post(
            reverse("api-v3-admin-add-entity"),
            {"entity_id": self.entity3.id, "name": "Admin Test", "category": "Administration"},
        )
        obj = Entity.objects.get(name="Admin Test")
        self.assertEquals(obj.entity_type, "Administration")

        # try to create with missing data
        response = self.client.post(reverse("api-v3-admin-add-entity"))
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api-v3-admin-add-entity"), {"category": "Producteur"})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            reverse("api-v3-admin-add-entity"), {"entity_id": self.entity3.id, "name": "Jean-Claude Test"}
        )
        self.assertEqual(response.status_code, 400)

        # try to enter wrong data
        response = self.client.post(
            reverse("api-v3-admin-add-entity"), {"category": "Boucher", "name": "Boucherie du Marais"}
        )
        self.assertEqual(response.status_code, 400)
