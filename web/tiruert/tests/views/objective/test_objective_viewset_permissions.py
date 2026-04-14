from django.test import TestCase

from core.models import ExternalAdminRights
from core.permissions import HasAdminRights
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
                # Admin actions require HasAdminRights with TIRIB_STATS
                (
                    ["get_objectives_admin_view", "get_agregated_objectives_admin_view"],
                    [HasAdminRights(allow_external=[ExternalAdminRights.TIRIB_STATS])],
                ),
                # Regular actions require HasTiruertRightsObjectives (OPERATOR, PRODUCER, TRADER)
                (
                    ["get_objectives"],
                    [HasTiruertRightsObjectives()],
                ),
            ],
        )
