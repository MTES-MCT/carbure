from django.test import TestCase
from rest_framework.permissions import IsAuthenticated

from core.models import Entity, UserRights
from core.permissions import HasUserRights
from core.tests_utils import PermissionTestMixin
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
                    [HasUserRights([UserRights.ADMIN, UserRights.RW])],
                ),
                (
                    ["balance"],
                    [HasUserRights([UserRights.ADMIN, UserRights.RO, UserRights.RW])],
                ),
                (
                    ["list", "retrieve", "update", "partial_update", "filters", "declare_teneur"],
                    [IsAuthenticated(), HasUserRights(None, [Entity.OPERATOR])],
                ),
            ],
        )
