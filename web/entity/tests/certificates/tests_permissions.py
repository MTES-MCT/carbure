from django.test import TestCase

from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, HasAdminRights, HasUserRights, UserRightsFactory
from core.tests_utils import PermissionTestMixin
from entity.views.certificates.certificates import EntityCertificateViewSet


class CertificatePermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            EntityCertificateViewSet,
            [
                (
                    ["list", "retrieve"],
                    [
                        (
                            UserRightsFactory(entity_type=[Entity.PRODUCER, Entity.TRADER, Entity.OPERATOR])
                            | AdminRightsFactory(
                                allow_external=[ExternalAdminRights.DOUBLE_COUNTING, ExternalAdminRights.TRANSFERRED_ELEC]
                            )
                        )()
                    ],
                ),
                (
                    ["add", "delete", "set_default", "update_certificate"],
                    [
                        HasUserRights(
                            entity_type=[Entity.PRODUCER, Entity.TRADER, Entity.OPERATOR],
                            role=[UserRights.RW, UserRights.ADMIN],
                        )
                    ],
                ),
                (
                    ["check_entity", "reject_entity"],
                    [
                        HasAdminRights(
                            allow_external=[ExternalAdminRights.DOUBLE_COUNTING],
                            allow_role=[UserRights.RW, UserRights.ADMIN],
                        )
                    ],
                ),
            ],
        )
