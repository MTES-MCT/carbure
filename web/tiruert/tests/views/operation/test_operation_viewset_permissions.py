from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from entity.permissions import HasDgddiWriteRights
from tiruert.permissions import HasTiruertRightsBalanceAndOperations, HasTiruertWriteRights
from tiruert.views.operation import OperationViewSet


class OperationViewSetPermissionsTest(TestCase, PermissionTestMixin):
    """Tests for OperationViewSet.get_permissions()."""

    def test_operation_viewset_permissions(self):
        """Test that OperationViewSet has correct permissions for each action."""
        self.assertViewPermissions(
            OperationViewSet,
            [
                # Write actions require HasTiruertWriteRights (OPERATOR, PRODUCER, TRADER with RW/ADMIN)
                (
                    [
                        "reject",
                        "accept",
                        "simulate",
                        "simulate_min_max",
                        "create",
                        "update",
                        "partial_update",
                        "destroy",
                        "export_operations_to_excel",
                        "declare_teneur",
                    ],
                    [HasTiruertWriteRights()],
                ),
                # Correct action requires HasDgddiWriteRights
                (
                    ["correct"],
                    [HasDgddiWriteRights()],
                ),
                # Read actions require HasTiruertRightsBalanceAndOperations OR HasDgddiWriteRights
                (
                    ["list", "retrieve", "balance", "filters", "filters_balance"],
                    [(HasTiruertRightsBalanceAndOperations | HasDgddiWriteRights)()],
                ),
            ],
        )
