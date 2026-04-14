from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from tiruert.permissions import HasTiruertRightsObjectives
from tiruert.views.objective import ObjectiveViewSet


class ObjectiveViewSetPermissionsTest(TestCase, PermissionTestMixin):
    """Tests for ObjectiveViewSet.get_permissions()."""

    def test_objective_viewset_permissions(self):
        """Test that ObjectiveViewSet has correct permissions for each action."""
        self.assertViewPermissions(
            ObjectiveViewSet,
            [
                # Retrieve objectives require HasTiruertRightsObjectives
                # (OPERATOR, PRODUCER, TRADER or ExternalAdmin.TIRIB_STATS)
                (
                    ["get_objectives"],
                    [HasTiruertRightsObjectives()],
                ),
            ],
        )
