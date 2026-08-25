from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from core.tests_utils import PermissionTestMixin
from h2.permissions import HasHRSRights, HasHRSWriteRights
from traceability.handlers.h2 import H2ActionHandler
from traceability.models import Action
from traceability.views.action import ActionViewset


class ActionViewsetPermissionTest(TestCase, PermissionTestMixin):
    def test_h2_permissions_when_industry_is_h2(self):
        view = ActionViewset()
        view.request = Request(APIRequestFactory().get("/", {"industry": Action.H2}))
        view.request.handler = H2ActionHandler()
        view.action = "list"

        self.assertPermissionsEqual(view.get_permissions(), [HasHRSRights()])

        view.action = "create"
        self.assertPermissionsEqual(view.get_permissions(), [HasHRSWriteRights()])
