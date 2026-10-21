from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from h2.handlers import H2ActionHandler
from h2.permissions import HasH2AdminRights, HasHRSRights, HasHRSWriteRights
from traceability.views.action import ActionViewset


class H2ActionPermissionViewSet(ActionViewset):
    def get_permissions(self):
        return H2ActionHandler().get_permissions(self.action)


class H2ActionHandlerPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            H2ActionPermissionViewSet,
            [
                (
                    ["list", "retrieve", "filters", "get_years", "download_import_template"],
                    [(HasHRSRights | HasH2AdminRights)()],
                ),
                (
                    ["destroy", "import_actions"],
                    [HasHRSWriteRights()],
                ),
            ],
        )
