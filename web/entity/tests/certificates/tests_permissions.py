from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, HasAdminRights, HasUserRights, UserRightsFactory
from core.tests_utils import PermissionTestMixin
from entity.permissions import HasCertificateRights, HasCertificateWriteRights
from entity.views.certificates.certificates import EntityCertificateViewSet


class SolidBiomassCertificatePermissionTest(SimpleTestCase):
    @patch("core.permissions.UserRights.objects.filter")
    def test_read_and_write_roles(self, filter_rights):
        entity = SimpleNamespace(id=42, entity_type=Entity.SOLID_BIOMASS_ENERGY_PRODUCER)
        user = SimpleNamespace(is_anonymous=False, is_verified=lambda: True)
        request = SimpleNamespace(user=user, entity=entity, session={})

        for role, can_write in [(UserRights.RO, False), (UserRights.RW, True), (UserRights.ADMIN, True)]:
            with self.subTest(role=role):
                filter_rights.return_value = [SimpleNamespace(entity_id=entity.id, role=role)]
                self.assertTrue(HasCertificateRights().has_permission(request, None))
                self.assertEqual(HasCertificateWriteRights().has_permission(request, None), can_write)


class CertificatePermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            EntityCertificateViewSet,
            [
                (
                    ["list", "retrieve"],
                    [
                        (
                            UserRightsFactory(
                                entity_type=[
                                    Entity.PRODUCER,
                                    Entity.TRADER,
                                    Entity.OPERATOR,
                                    Entity.POWER_OR_HEAT_PRODUCER,
                                    Entity.SOLID_BIOMASS_ENERGY_PRODUCER,
                                    Entity.BIOMETHANE_PRODUCER,
                                ]
                            )
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
                            entity_type=[
                                Entity.PRODUCER,
                                Entity.TRADER,
                                Entity.OPERATOR,
                                Entity.POWER_OR_HEAT_PRODUCER,
                                Entity.SOLID_BIOMASS_ENERGY_PRODUCER,
                                Entity.BIOMETHANE_PRODUCER,
                            ],
                            role=[UserRights.RW, UserRights.ADMIN],
                        )
                    ],
                ),
                (
                    ["check_entity", "reject_entity"],
                    [
                        HasAdminRights(
                            allow_external=[ExternalAdminRights.TRANSFERRED_ELEC, ExternalAdminRights.DOUBLE_COUNTING],
                            allow_role=[UserRights.RW, UserRights.ADMIN],
                        )
                    ],
                ),
            ],
        )
