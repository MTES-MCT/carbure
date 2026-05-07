from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from tiruert.permissions import HasTiruertRightsBalanceAndOperations, HasTiruertWriteRights, TiruertAdminRights
from tiruert.views.elec_operation import ElecOperationViewSet


class ElecOperationViewSetPermissionsTest(TestCase, PermissionTestMixin):
    """Tests for ElecOperationViewSet.get_permissions()."""

    def test_elec_operation_viewset_permissions(self):
        """Validate permissions per action."""
        self.assertViewPermissions(
            ElecOperationViewSet,
            [
                (
                    ["reject", "accept", "create", "destroy"],
                    [HasTiruertWriteRights()],
                ),
                (
                    ["list", "retrieve", "update", "partial_update", "filters", "declare_teneur", "balance"],
                    [(HasTiruertRightsBalanceAndOperations | TiruertAdminRights)()],
                ),
            ],
        )
