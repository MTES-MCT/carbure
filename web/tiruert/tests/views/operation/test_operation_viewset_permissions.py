from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from entity.permissions import HasDgddiWriteRights, HasOperatorRights, HasOperatorWriteRights
from tiruert.views.operation import OperationViewSet


class OperationViewSetPermissionsTest(TestCase, PermissionTestMixin):
    """Tests for OperationViewSet.get_permissions()."""

    def test_operation_viewset_permissions(self):
        """Test that OperationViewSet has correct permissions for each action."""
        self.assertViewPermissions(
            OperationViewSet,
            [
                # Write actions require HasOperatorWriteRights
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
                    [HasOperatorWriteRights()],
                ),
                # Correct action requires HasDgddiWriteRights
                (
                    ["correct"],
                    [HasDgddiWriteRights()],
                ),
                # Read actions require HasOperatorRights OR HasDgddiWriteRights
                (
                    ["list", "retrieve", "balance", "filters", "filters_balance"],
                    [(HasOperatorRights | HasDgddiWriteRights)()],
                ),
            ],
        )
