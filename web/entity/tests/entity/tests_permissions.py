from django.test import TestCase

from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import HasAdminRights, HasUserRights
from core.tests_utils import PermissionTestMixin
from entity.views.entity import EntityViewSet


class EntityPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            EntityViewSet,
            [
                (
                    ["list", "retrieve"],
                    [
                        HasAdminRights(
                            allow_external=[
                                ExternalAdminRights.AIRLINE,
                                ExternalAdminRights.ELEC,
                                ExternalAdminRights.DOUBLE_COUNTING,
                                ExternalAdminRights.TRANSFERRED_ELEC,
                                ExternalAdminRights.DREAL,
                            ]
                        )
                    ],
                ),
                (
                    ["create"],
                    [
                        HasAdminRights(
                            allow_role=[UserRights.RW, UserRights.ADMIN],
                            allow_external=[
                                ExternalAdminRights.AIRLINE,
                                ExternalAdminRights.ELEC,
                                ExternalAdminRights.DOUBLE_COUNTING,
                            ],
                        )
                    ],
                ),
                (
                    ["enable_entity"],
                    [
                        HasAdminRights(
                            allow_external=[ExternalAdminRights.AIRLINE, ExternalAdminRights.ELEC],
                            allow_role=[UserRights.RW, UserRights.ADMIN],
                        )
                    ],
                ),
                (
                    ["get_entity_stats", "update_entity_info"],
                    [HasUserRights(role=[UserRights.ADMIN, UserRights.RW])],
                ),
                (
                    ["direct_deliveries", "elec", "preferred_unit", "release_for_consumption", "stocks", "trading"],
                    [
                        HasUserRights(
                            entity_type=[Entity.PRODUCER, Entity.OPERATOR, Entity.TRADER],
                            role=[UserRights.ADMIN, UserRights.RW],
                        )
                    ],
                ),
            ],
        )
