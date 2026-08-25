from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from h2.handlers import H2ActionHandler
from h2.permissions import HasHRSRights, HasHRSWriteRights


class H2ActionHandlerPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        handler = H2ActionHandler()

        for action in ["list", "retrieve"]:
            with self.subTest(action=action):
                self.assertPermissionsEqual(handler.get_permissions(action), [HasHRSRights()])

        for action in ["create", "update", "partial_update", "destroy"]:
            with self.subTest(action=action):
                self.assertPermissionsEqual(handler.get_permissions(action), [HasHRSWriteRights()])
