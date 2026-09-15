from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity, ExternalAdminRights, UserRights, UserRightsRequests
from core.tests_utils import setup_current_user
from entity.factories.entity import EntityFactory

User = get_user_model()


class TestAdminRightsRequestScope(TestCase):
    """ExternalAdmin must not approve, reject or change roles for entities outside its scope."""

    fixtures = ["json/countries.json"]

    @classmethod
    def setUpTestData(cls):
        cls.airline_admin = EntityFactory.create(name="Airline admin", entity_type=Entity.EXTERNAL_ADMIN)
        ExternalAdminRights.objects.create(entity=cls.airline_admin, right=ExternalAdminRights.AIRLINE)

        cls.airline = EntityFactory.create(name="Airline company", entity_type=Entity.AIRLINE)
        cls.producer = EntityFactory.create(name="Out of scope producer", entity_type=Entity.PRODUCER)

    def setUp(self):
        setup_current_user(
            self,
            email="airline-admin@carbure.local",
            name="Airline Admin",
            password="gogogo",
            entity_rights=[(self.airline_admin, UserRights.ADMIN)],
        )
        self.target_user = User.objects.create_user(
            email="target@carbure.local",
            name="Target user",
            password="gogogo",
        )
        self.mail_patcher = patch("entity.views.users.mixins.update_right_request.send_mail")
        self.mail_patcher.start()
        self.addCleanup(self.mail_patcher.stop)

    def update_right_request(self, right_request_id, request_status):
        url = reverse("api-entity-users-update-right-request")
        return self.client.post(
            url,
            {"id": right_request_id, "status": request_status},
            query_params={"entity_id": self.airline_admin.pk},
        )

    def update_user_role(self, right_request_id, role):
        url = reverse("api-entity-users-update-user-role")
        return self.client.post(
            url,
            {"request_id": right_request_id, "role": role},
            query_params={"entity_id": self.airline_admin.pk},
        )

    def list_rights_requests(self, **params):
        url = reverse("api-entity-users-rights-requests")
        return self.client.get(url, {"entity_id": self.airline_admin.pk, **params})

    def create_right_request(self, entity, request_status="PENDING", role=UserRights.RO):
        return UserRightsRequests.objects.create(
            user=self.target_user,
            entity=entity,
            role=role,
            status=request_status,
        )

    def test_cannot_accept_right_request_of_another_entity(self):
        right_request = self.create_right_request(self.producer)

        response = self.update_right_request(right_request.pk, "ACCEPTED")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        right_request.refresh_from_db()
        self.assertEqual(right_request.status, "PENDING")
        self.assertFalse(UserRights.objects.filter(user=self.target_user, entity=self.producer).exists())

    def test_cannot_reject_right_request_of_another_entity(self):
        right_request = self.create_right_request(self.producer)

        response = self.update_right_request(right_request.pk, "REJECTED")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        right_request.refresh_from_db()
        self.assertEqual(right_request.status, "PENDING")

    def test_cannot_change_role_of_another_entity(self):
        right_request = self.create_right_request(self.producer, request_status="ACCEPTED", role=UserRights.RO)
        user_right = UserRights.objects.create(user=self.target_user, entity=self.producer, role=UserRights.RO)

        response = self.update_user_role(right_request.pk, UserRights.ADMIN)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        right_request.refresh_from_db()
        user_right.refresh_from_db()
        self.assertEqual(right_request.role, UserRights.RO)
        self.assertEqual(user_right.role, UserRights.RO)

    def test_can_accept_right_request_in_scope(self):
        right_request = self.create_right_request(self.airline)

        response = self.update_right_request(right_request.pk, "ACCEPTED")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        right_request.refresh_from_db()
        self.assertEqual(right_request.status, "ACCEPTED")
        self.assertTrue(UserRights.objects.filter(user=self.target_user, entity=self.airline, role=UserRights.RO).exists())

    def test_can_change_role_in_scope(self):
        right_request = self.create_right_request(self.airline, request_status="ACCEPTED", role=UserRights.RO)
        user_right = UserRights.objects.create(user=self.target_user, entity=self.airline, role=UserRights.RO)

        response = self.update_user_role(right_request.pk, UserRights.ADMIN)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        right_request.refresh_from_db()
        user_right.refresh_from_db()
        self.assertEqual(right_request.role, UserRights.ADMIN)
        self.assertEqual(user_right.role, UserRights.ADMIN)

    def test_rights_requests_are_limited_to_external_admin_scope(self):
        in_scope_request = self.create_right_request(self.airline)
        out_of_scope_request = self.create_right_request(self.producer)

        response = self.list_rights_requests()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([request["id"] for request in response.data], [in_scope_request.id])
        self.assertNotIn(out_of_scope_request.id, [request["id"] for request in response.data])

    def test_forged_company_id_cannot_expand_external_admin_scope(self):
        out_of_scope_request = self.create_right_request(self.producer)

        response = self.list_rights_requests(company_id=self.producer.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        self.assertNotIn(out_of_scope_request.id, [request["id"] for request in response.data])
