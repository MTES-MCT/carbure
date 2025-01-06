from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Entity, UserRights, UserRightsRequests
from core.tests_utils import setup_current_user


class Endpoint:
    change_user_role = reverse("entity-users-change-role")
    invite_user = reverse("entity-users-invite-user")


User = get_user_model()


class EntityUserTest(TestCase):
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

        url = "entity-users-revoke-access"
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "email": self.user2.email})
        assert response.status_code == 403

    def test_change_user_role_missing_params(self):
        res = self.client.post(
            Endpoint.change_user_role,
            {"email": self.user.email, "entity_id": self.trader.id},
        )
        assert res.status_code == 400
        data = res.json()
        assert data["error"] == "UPDATE_FAILED"
        assert data["data"]["role"] is not None

    def test_change_user_role_missing_user(self):
        res = self.client.post(
            Endpoint.change_user_role,
            {
                "email": "missing@carbure.test",
                "entity_id": self.trader.id,
                "role": "RW",
            },
        )
        assert res.status_code == 400
        data = res.json()
        assert data["error"] == "MISSING_USER"

    def test_change_user_role_no_prior_rights(self):
        other_user = User.objects.create(email="other@carbure.test", name="Other", password="other")
        res = self.client.post(
            Endpoint.change_user_role,
            {"email": other_user.email, "entity_id": self.trader.id, "role": "RW"},
        )
        assert res.status_code == 400
        data = res.json()
        assert data["error"] == "NO_PRIOR_RIGHTS"

    def test_change_user_role_ok(self):
        user_right = UserRights.objects.get(user=self.user, entity=self.trader)
        assert user_right.role == "ADMIN"
        res = self.client.post(
            Endpoint.change_user_role,
            {"email": self.user.email, "entity_id": self.trader.id, "role": "RW"},
        )
        assert res.status_code == 200
        user_right = UserRights.objects.get(user=self.user, entity=self.trader)
        assert user_right.role == "RW"

    def test_invite_user_new_user_success(self):
        params = {
            "entity_id": self.entity1.id,
            "email": "newuser@carbure.local",
            "role": UserRights.ADMIN,
        }
        res = self.client.post(Endpoint.invite_user, params)
        assert res.status_code == 200
        new_user = User.objects.get(email="newuser@carbure.local")
        assert new_user is not None
        assert (
            UserRightsRequests.objects.filter(
                user_id=new_user.id, entity_id=self.entity1.id, role=UserRights.ADMIN, status="ACCEPTED"
            ).count()
            == 1
        )
        assert UserRights.objects.filter(user_id=new_user.id, entity_id=self.entity1.id, role=UserRights.ADMIN).count() == 1

    def test_invite_user_missing_params(self):
        params = {
            "entity_id": self.entity1.id,
            "email": "newuser@carbure.local",
        }
        res = self.client.post(Endpoint.invite_user, params)
        assert res.status_code == 400
        data = res.json()
        assert data["error"] == "INVITE_FAILED"
        assert data["data"]["role"] is not None

    def test_invite_user_bad_email(self):
        params = {
            "entity_id": self.entity1.id,
            "email": "newuser@carbure",
            "role": UserRights.ADMIN,
        }
        res = self.client.post(Endpoint.invite_user, params)
        assert res.status_code == 400
        data = res.json()
        assert data["error"] == "INVITE_FAILED"
        assert data["data"]["email"] is not None

    def test_invite_user_already_granted(self):
        params = {
            "entity_id": self.entity1.id,
            "email": self.user.email,
            "role": UserRights.RW,
        }
        res = self.client.post(Endpoint.invite_user, params)
        assert res.status_code == 400
        data = res.json()
        assert data["error"] == "ACCESS_ALREADY_GIVEN"

    def test_invite_user_existing_user_success(self):
        params = {
            "entity_id": self.entity1.id,
            "email": self.user2.email,
            "role": UserRights.ADMIN,
        }
        res = self.client.post(Endpoint.invite_user, params)
        assert res.status_code == 200
        new_user = User.objects.get(email=self.user2.email)
        assert new_user is not None
        assert (
            UserRightsRequests.objects.filter(
                user_id=new_user.id, entity_id=self.entity1.id, role=UserRights.ADMIN, status="ACCEPTED"
            ).count()
            == 1
        )
        assert UserRights.objects.filter(user_id=new_user.id, entity_id=self.entity1.id, role=UserRights.ADMIN).count() == 1
