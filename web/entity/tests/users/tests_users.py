import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from auth.tokens import account_activation_token
from core.models import Entity, UserRights, UserRightsRequests
from core.tests_utils import setup_current_user


class Endpoint:
    change_user_role = reverse("api-entity-users-change-role")
    invite_user = reverse("api-entity-users-invite-user")
    accept_user = reverse("api-entity-users-accept-user")


User = get_user_model()


class EntityUserTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]

        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "ADMIN")], True)

        user_model = get_user_model()
        self.user2 = user_model.objects.create_user(
            email="testuser2@toto.com", name="Le Super Testeur 2", password="totopouet"
        )

        self.entity1, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity1, defaults={"role": UserRights.ADMIN})

        self.trader = Entity.objects.create(name="Test entity", entity_type=Entity.TRADER)
        UserRights.objects.update_or_create(user=self.user, entity=self.trader, defaults={"role": UserRights.ADMIN})

    def test_revoke_access(self):
        # try invite/revoke as non-admin
        right = UserRights.objects.get(entity=self.entity1, user=self.user)
        right.role = UserRights.RO
        right.save()

        url = reverse("api-entity-users-revoke-access")
        response = self.client.post(
            f"{url}?entity_id={self.entity1.id}", {"entity_id": self.entity1.id, "email": self.user2.email}
        )
        self.assertEqual(response.status_code, 403)

    def test_change_user_role_missing_params(self):
        res = self.client.post(
            f"{Endpoint.change_user_role}?entity_id={self.trader.id}",
            {"email": self.user.email, "entity_id": self.trader.id},
        )
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIsNotNone(data["role"])

    def test_change_user_role_missing_user(self):
        res = self.client.post(
            f"{Endpoint.change_user_role}?entity_id={self.trader.id}",
            {
                "email": "missing@carbure.test",
                "entity_id": self.trader.id,
                "role": "RW",
            },
        )
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIsNotNone(data["email"])

    def test_change_user_role_no_prior_rights(self):
        other_user = User.objects.create(email="other@carbure.test", name="Other", password="other")
        res = self.client.post(
            f"{Endpoint.change_user_role}?entity_id={self.trader.id}",
            {"email": other_user.email, "entity_id": self.trader.id, "role": "RW"},
        )
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data["message"], "NO_PRIOR_RIGHTS")

    def test_change_user_role_ok(self):
        user_right = UserRights.objects.get(user=self.user, entity=self.trader)
        self.assertEqual(user_right.role, "ADMIN")
        res = self.client.post(
            f"{Endpoint.change_user_role}?entity_id={self.trader.id}",
            {"email": self.user.email, "entity_id": self.trader.id, "role": "RW"},
        )
        self.assertEqual(res.status_code, 200)
        user_right = UserRights.objects.get(user=self.user, entity=self.trader)
        self.assertEqual(user_right.role, "RW")

    def test_invite_user_new_user_success(self):
        params = {
            "entity_id": self.entity1.id,
            "email": "newuser@carbure.local",
            "role": UserRights.ADMIN,
        }
        res = self.client.post(f"{Endpoint.invite_user}?entity_id={self.entity1.id}", params)
        self.assertEqual(res.status_code, 200)
        new_user = User.objects.get(email="newuser@carbure.local")
        self.assertIsNotNone(new_user)
        self.assertFalse(new_user.has_usable_password())
        self.assertIn("invite=1", mail.outbox[0].body)
        self.assertEqual(
            UserRightsRequests.objects.filter(
                user_id=new_user.id, entity_id=self.entity1.id, role=UserRights.ADMIN, status="ACCEPTED"
            ).count(),
            1,
        )
        self.assertEqual(
            UserRights.objects.filter(user_id=new_user.id, entity_id=self.entity1.id, role=UserRights.ADMIN).count(),
            1,
        )

    def test_invite_user_missing_params(self):
        params = {
            "entity_id": self.entity1.id,
            "email": "newuser@carbure.local",
        }
        res = self.client.post(f"{Endpoint.invite_user}?entity_id={self.entity1.id}", params)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIsNotNone(data["role"])

    def test_invite_user_bad_email(self):
        params = {
            "entity_id": self.entity1.id,
            "email": "newuser@carbure",
            "role": UserRights.ADMIN,
        }
        res = self.client.post(f"{Endpoint.invite_user}?entity_id={self.entity1.id}", params)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIsNotNone(data["email"])

    def test_invite_user_already_granted(self):
        params = {
            "entity_id": self.entity1.id,
            "email": self.user.email,
            "role": UserRights.RW,
        }
        res = self.client.post(f"{Endpoint.invite_user}?entity_id={self.entity1.id}", params)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data["message"], "ACCESS_ALREADY_GIVEN")

    def test_invite_user_existing_user_success(self):
        params = {
            "entity_id": self.entity1.id,
            "email": self.user2.email,
            "role": UserRights.ADMIN,
        }
        res = self.client.post(f"{Endpoint.invite_user}?entity_id={self.entity1.id}", params)
        self.assertEqual(res.status_code, 200)
        new_user = User.objects.get(email=self.user2.email)
        self.assertIsNotNone(new_user)
        self.assertEqual(
            UserRightsRequests.objects.filter(
                user_id=new_user.id, entity_id=self.entity1.id, role=UserRights.ADMIN, status="ACCEPTED"
            ).count(),
            1,
        )
        self.assertEqual(
            UserRights.objects.filter(user_id=new_user.id, entity_id=self.entity1.id, role=UserRights.ADMIN).count(),
            1,
        )

    def test_second_invite_of_pending_user_keeps_the_first_link(self):
        res = self.client.post(
            f"{Endpoint.invite_user}?entity_id={self.entity1.id}",
            {"email": "pending@carbure.local", "role": UserRights.RO},
        )
        self.assertEqual(res.status_code, 200)
        pending = User.objects.get(email="pending@carbure.local")
        token = re.search(r"token=([^&\s]+)", mail.outbox[0].body).group(1)

        res = self.client.post(
            f"{Endpoint.invite_user}?entity_id={self.trader.id}",
            {"email": "pending@carbure.local", "role": UserRights.RW},
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        pending.refresh_from_db()
        self.assertTrue(account_activation_token.check_token(pending, token))
        self.assertTrue(UserRights.objects.filter(user=pending, entity=self.trader, role=UserRights.RW).exists())

    def test_grant_access(self):
        right_request = UserRightsRequests.objects.create(user=self.user2, entity=self.trader, role=UserRights.ADMIN)

        response = self.client.post(f"{Endpoint.accept_user}?entity_id={self.admin.pk}", {"request_id": right_request.id})
        self.assertEqual(response.status_code, 403)

        response = self.client.post(f"{Endpoint.accept_user}?entity_id={self.trader.pk}", {"request_id": right_request.id})
        self.assertEqual(response.status_code, 200)
