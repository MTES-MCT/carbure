from django.test import TestCase

from core.models import UserRights
from core.permissions import HasAdminRights, HasUserRights
from core.tests_utils import PermissionTestMixin
from entity.views.depots.depots import DepotViewSet


class DepotPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            DepotViewSet,
            [
                (
                    ["list"],
                    [(HasUserRights | HasAdminRights)()],
                ),
                (
                    ["add", "create_depot", "delete_depot"],
                    [HasUserRights(role=[UserRights.ADMIN, UserRights.RW])],
                ),
            ],
        )
