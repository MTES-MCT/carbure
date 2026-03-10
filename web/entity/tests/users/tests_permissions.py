from django.test import TestCase

from biomethane.permissions import HasDrealRights
from core.models import ExternalAdminRights, UserRights
from core.permissions import HasAdminRights, UserRightsFactory
from core.tests_utils import PermissionTestMixin
from entity.views.users.users import UserViewSet


class UserPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            UserViewSet,
            [
                (
                    ["entity_rights_requests", "accept_user", "change_role", "invite_user", "revoke_access"],
                    [
                        (
                            HasDrealRights
                            | UserRightsFactory(
                                role=[UserRights.ADMIN],
                            )
                        )()
                    ],
                ),
                (
                    ["update_right_request", "update_user_role"],
                    [
                        HasAdminRights(
                            allow_role=[UserRights.RW, UserRights.ADMIN],
                            allow_external=[
                                ExternalAdminRights.AIRLINE,
                                ExternalAdminRights.ELEC,
                                ExternalAdminRights.DOUBLE_COUNTING,
                                ExternalAdminRights.DREAL,
                            ],
                        )
                    ],
                ),
                (
                    ["rights_requests"],
                    [
                        HasAdminRights(
                            allow_external=[
                                ExternalAdminRights.AIRLINE,
                                ExternalAdminRights.ELEC,
                                ExternalAdminRights.TRANSFERRED_ELEC,
                                ExternalAdminRights.DOUBLE_COUNTING,
                                ExternalAdminRights.DREAL,
                            ]
                        )
                    ],
                ),
            ],
        )
