import json
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.validators import UniqueValidator

from core.models import Entity
from core.permissions import HasEntityWriteRights
from core.tests_utils import setup_current_user
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.registry import ACTION_HANDLERS
from traceability.models import Action, ActionStatus
from traceability.views.action import ActionViewset


def is_holder(actor, holder, parent_holder):
    return actor == holder


class GenericActionHandler(ActionIndustryHandler):
    industry = Action.H2
    action_creation_flow = ((None, (Action.INIT, ActionStatus.PENDING)),)
    action_status_authorizations = {Action.INIT: {(ActionStatus.PENDING,): is_holder}}


@patch.dict(ACTION_HANDLERS, {GenericActionHandler.industry: GenericActionHandler})
class ActionCreateTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.holder = Entity(id=1, entity_type=Entity.OPERATOR)
        self.view = ActionViewset.as_view({"post": "create"})
        self.payload = {
            "type": Action.INIT,
            "status": ActionStatus.PENDING,
            "holder": self.holder.id,
            "pos_id": "POS-1",
            "quantity": "12.500",
            "working_date": "2026-01-01",
        }

    def post(self, data):
        request = self.factory.post(f"/actions/?industry={GenericActionHandler.industry}", data, format="json")
        request.entity = self.holder
        force_authenticate(request, user=Mock())
        queryset = Mock()
        queryset.get.return_value = self.holder
        with (
            patch.object(ActionViewset, "get_permissions", return_value=[]),
            patch.object(PrimaryKeyRelatedField, "get_queryset", new=lambda field: queryset),
            patch.object(UniqueValidator, "__call__", return_value=None),
        ):
            return self.view(request)

    def test_request_matching_flow_validates_action_data(self):
        response = self.post(
            {"type": Action.INIT, "status": ActionStatus.PENDING, "holder": self.holder.id, "quantity": "invalid"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)
        self.assertIn("pos_id", response.data)

    def test_missing_serializer_is_reported_as_validation_error(self):
        with patch.object(GenericActionHandler, "get_action_creation_serializers", return_value={}):
            response = self.post({"type": Action.INIT, "status": ActionStatus.PENDING, "holder": self.holder.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)

    def test_unknown_creation_edge_returns_validation_error(self):
        response = self.post({"type": Action.VALORIZE, "status": ActionStatus.CREATED, "holder": self.holder.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields_returns_validation_error(self):
        response = self.post({})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)
        self.assertIn("holder", response.data)
        self.assertIn("status", response.data)

    def test_create_uses_the_write_permission(self):
        permission = GenericActionHandler.get_permissions("create")[0]
        self.assertIsInstance(permission, HasEntityWriteRights)

    def test_missing_status_authorization_refuses_creation(self):
        with patch.object(GenericActionHandler, "action_status_authorizations", {}):
            response = self.post(self.payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_specific_predicate_receives_holders_and_refuses_without_fallback(self):
        default = Mock(return_value=True)
        specific = Mock(return_value=False)
        with (
            patch.object(
                ActionIndustryHandler, "action_status_authorizations", {Action.INIT: {(ActionStatus.PENDING,): default}}
            ),
            patch.object(
                GenericActionHandler, "action_status_authorizations", {Action.INIT: {(ActionStatus.PENDING,): specific}}
            ),
        ):
            response = self.post({**self.payload, "industry": "OTHER"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        default.assert_not_called()
        specific.assert_called_once_with(self.holder, self.holder, None)

    def test_creation_uses_default_authorization(self):
        default = Mock(return_value=False)
        with (
            patch.object(
                ActionIndustryHandler, "action_status_authorizations", {Action.INIT: {(ActionStatus.PENDING,): default}}
            ),
            patch.object(GenericActionHandler, "action_status_authorizations", {}),
        ):
            response = self.post(self.payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        default.assert_called_once_with(self.holder, self.holder, None)


@patch.dict(ACTION_HANDLERS, {GenericActionHandler.industry: GenericActionHandler})
class ActionCreateIntegrationTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.holder = Entity.objects.create(name="Opérateur", entity_type=Entity.OPERATOR)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.holder, "RW")])
        self.url = reverse("traceability-action-list")
        self.params = {"entity_id": self.holder.id, "industry": GenericActionHandler.industry}
        self.payload = {
            "type": Action.INIT,
            "status": ActionStatus.PENDING,
            "holder": self.holder.id,
            "pos_id": "POS-1",
            "quantity": "12.500",
            "working_date": "2026-01-01",
            "material": None,
            "site": None,
        }

    def post(self, payload):
        return self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json", query_params=self.params
        )

    def test_creates_action_and_status(self):
        response = self.post(self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        action = Action.objects.get(pk=response.data["id"])
        self.assertEqual(action.type, Action.INIT)
        self.assertEqual(action.industry, GenericActionHandler.industry)
        self.assertEqual(action.holder, self.holder)
        self.assertIsNone(action.parent)
        self.assertEqual(action.status, ActionStatus.PENDING)
        self.assertEqual(response.data["status"], ActionStatus.PENDING)
        self.assertEqual(ActionStatus.objects.filter(action=action).count(), 1)

    def test_status_without_matching_edge_does_not_create_action(self):
        response = self.post({**self.payload, "status": ActionStatus.ACCEPTED})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Action.objects.exists())

    def test_unauthorized_holder_does_not_create_action(self):
        other = Entity.objects.create(name="Autre opérateur", entity_type=Entity.OPERATOR)
        response = self.post({**self.payload, "holder": other.pk})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Action.objects.exists())
        self.assertFalse(ActionStatus.objects.exists())

    def test_status_creation_failure_rolls_back_action(self):
        with patch.object(ActionStatus.objects, "create", side_effect=RuntimeError("status failure")):
            with self.assertRaisesMessage(RuntimeError, "status failure"):
                self.post(self.payload)

        self.assertFalse(Action.objects.exists())
