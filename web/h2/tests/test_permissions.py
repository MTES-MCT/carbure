from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from h2.permissions import HasHRSRights, HasHRSWriteRights
from h2.views import H2StationViewSet


class H2StationPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            H2StationViewSet,
            [
                (
                    ["list", "retrieve"],
                    [HasHRSRights()],
                ),
                (
                    ["create", "update", "partial_update", "destroy"],
                    [HasHRSWriteRights()],
                ),
            ],
        )
