from contextlib import nullcontext
from unittest.mock import Mock, patch

from django.http import Http404
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from core.models import Entity, ExternalAdminRights
from core.tests_utils import PermissionTestMixin, setup_current_user
from h2.handlers.action import H2ActionHandler
from h2.permissions import HasH2AdminRights, HasHRSWriteRights
from traceability.factories import ActionFactory
from traceability.handlers.action import ActionIndustryHandler
from traceability.models import Action, ActionStatus
from traceability.views.action import ActionViewset


class ActionStatusTest(SimpleTestCase, PermissionTestMixin):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.actor = Entity(id=1, entity_type=Entity.ADMIN)
        self.holder = Entity(id=2, entity_type=Entity.HRS)
        self.action = Action(id=3, holder=self.holder, industry=Action.H2, type=Action.INIT)
        self.action.status = ActionStatus.PENDING
        self.url = reverse("traceability-action-status", args=[self.action.pk])
        self.view = ActionViewset.as_view({"post": "status"})

    def post(self, data, actor=None, lookup_error=None):
        request = self.factory.post(f"{self.url}?industry={Action.H2}", data, format="json")
        request.entity = actor or self.actor
        force_authenticate(request, user=Mock())
        with (
            patch.object(ActionViewset, "get_permissions", return_value=[]),
            patch.object(ActionViewset, "get_object", return_value=self.action, side_effect=lookup_error),
            patch("traceability.views.action.transaction.atomic", return_value=nullcontext()),
            patch.object(Entity, "has_external_admin_right", return_value=False),
            patch.object(ActionStatus.objects, "create") as create_status,
        ):
            response = self.view(request, pk=self.action.pk)
        return response, create_status

    def test_admin_can_accept_reject_or_block_pending_init(self):
        for target in (ActionStatus.ACCEPTED, ActionStatus.REJECTED, ActionStatus.BLOCKED):
            with self.subTest(status=target):
                response, create_status = self.post({"status": target})

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data, {"status": target})
                create_status.assert_called_once_with(action=self.action, status=target)

    def test_refuses_invalid_or_missing_status(self):
        for data in ({}, {"status": "UNKNOWN"}, {"status": None}):
            with self.subTest(data=data):
                response, create_status = self.post(data)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("status", response.data)
                create_status.assert_not_called()

    def test_refuses_changes_from_terminal_statuses(self):
        for current in (ActionStatus.ACCEPTED, ActionStatus.BLOCKED, ActionStatus.DELETED):
            with self.subTest(status=current):
                self.action.status = current
                response, create_status = self.post({"status": ActionStatus.REJECTED})

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                create_status.assert_not_called()

    def test_refuses_status_without_rule_even_if_transition_exists(self):
        response, create_status = self.post({"status": ActionStatus.DELETED})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        create_status.assert_not_called()

    def test_refuses_holder_without_admin_right(self):
        response, create_status = self.post({"status": ActionStatus.ACCEPTED}, actor=self.holder)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        create_status.assert_not_called()

    def test_authorizes_using_stored_type_and_holders(self):
        parent_holder = Entity(id=4, entity_type=Entity.HRS)
        self.action.parent = Action(id=5, holder=parent_holder, industry=Action.H2, type=Action.INIT)
        authorize = Mock(return_value=True)
        with patch.object(
            H2ActionHandler, "action_status_authorizations", {Action.INIT: {(ActionStatus.ACCEPTED,): authorize}}
        ):
            response, create_status = self.post(
                {"status": ActionStatus.ACCEPTED, "type": Action.VALORIZE, "holder": self.actor.pk, "parent": None}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authorize.assert_called_once_with(self.actor, self.holder, parent_holder)
        create_status.assert_called_once_with(action=self.action, status=ActionStatus.ACCEPTED)

    def test_uses_base_authorization(self):
        authorize = Mock(return_value=True)
        with (
            patch.object(
                ActionIndustryHandler, "action_status_authorizations", {Action.INIT: {(ActionStatus.ACCEPTED,): authorize}}
            ),
            patch.object(H2ActionHandler, "action_status_authorizations", {}),
        ):
            response, create_status = self.post({"status": ActionStatus.ACCEPTED})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authorize.assert_called_once_with(self.actor, self.holder, None)
        create_status.assert_called_once()

    def test_returns_not_found_for_inaccessible_action(self):
        response, create_status = self.post({"status": ActionStatus.ACCEPTED}, lookup_error=Http404())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        create_status.assert_not_called()

    def test_requires_write_permission(self):
        self.assertPermissionsEqual(
            H2ActionHandler.get_permissions("status"),
            [HasHRSWriteRights()],
        )


class ActionStatusIntegrationTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.holder = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        self.admin = Entity.objects.create(name="H2 admin", entity_type=Entity.EXTERNAL_ADMIN)
        ExternalAdminRights.objects.create(entity=self.admin, right=ExternalAdminRights.H2)
        setup_current_user(self, "admin@carbure.local", "Admin", "password", [(self.admin, "RW")])
        self.action = ActionFactory.create(
            holder=self.holder, industry=Action.H2, type=Action.INIT, status=ActionStatus.PENDING, material=None, site=None
        )
        self.url = reverse("traceability-action-status", args=[self.action.pk])

    def post(self, target, entity=None):
        return self.client.post(
            self.url,
            {"status": target},
            content_type="application/json",
            query_params={"entity_id": (entity or self.admin).pk, "industry": Action.H2},
        )

    @patch.object(H2ActionHandler, "write_permission", HasHRSWriteRights | HasH2AdminRights)
    def test_appends_history_and_refuses_second_transition_from_accepted(self):
        response = self.post(ActionStatus.ACCEPTED)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Action.objects.get(pk=self.action.pk).status, ActionStatus.ACCEPTED)
        self.assertEqual(
            list(self.action.action_statuses.values_list("status", flat=True)),
            [ActionStatus.PENDING, ActionStatus.ACCEPTED],
        )

        response = self.post(ActionStatus.REJECTED)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.action.action_statuses.count(), 2)

    @patch.object(H2ActionHandler, "write_permission", HasHRSWriteRights | HasH2AdminRights)
    def test_cannot_change_action_from_another_industry(self):
        Action.unannotated.filter(pk=self.action.pk).update(industry="OTHER")

        response = self.post(ActionStatus.ACCEPTED)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.action.action_statuses.count(), 1)

    def test_cannot_change_inaccessible_action(self):
        other = Entity.objects.create(name="Other HRS", entity_type=Entity.HRS)
        setup_current_user(self, "writer@carbure.local", "Writer", "password", [(other, "RW")])

        response = self.post(ActionStatus.ACCEPTED, entity=other)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.action.action_statuses.count(), 1)

    def test_read_only_holder_cannot_change_status(self):
        setup_current_user(self, "reader@carbure.local", "Reader", "password", [(self.holder, "RO")])

        response = self.post(ActionStatus.ACCEPTED, entity=self.holder)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.action.action_statuses.count(), 1)

    def test_admin_without_write_permission_cannot_change_status(self):
        response = self.post(ActionStatus.ACCEPTED)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.action.action_statuses.count(), 1)
