from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.test import APIRequestFactory, force_authenticate

from core.models import Entity
from h2.handlers.action import H2ActionHandler
from h2.permissions import HasHRSWriteRights
from traceability.models import Action
from traceability.views.action import ActionViewset


class ActionCreateTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.holder = Entity(id=1, entity_type=Entity.HRS)
        self.view = ActionViewset.as_view({"post": "create"})

    def post(self, data):
        request = self.factory.post("/actions/?industry=H2", data, format="json")
        request.entity = self.holder
        force_authenticate(request, user=Mock())
        queryset = Mock()
        queryset.get.return_value = self.holder
        with (
            patch.object(ActionViewset, "get_permissions", return_value=[]),
            patch.object(PrimaryKeyRelatedField, "get_queryset", new=lambda field: queryset),
        ):
            return self.view(request)

    def test_authorized_request_does_not_create_an_action_yet(self):
        response = self.post({"type": Action.INIT, "holder": self.holder.id})

        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

    def test_unauthorized_request_returns_validation_error(self):
        response = self.post({"type": Action.VALORIZE, "holder": self.holder.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields_returns_validation_error(self):
        response = self.post({})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)
        self.assertIn("holder", response.data)

    def test_create_uses_the_write_permission(self):
        permission = H2ActionHandler.get_permissions("create")[0]
        self.assertIsInstance(permission, HasHRSWriteRights)
