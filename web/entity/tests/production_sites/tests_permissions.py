from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from doublecount.permissions import HasDoubleCountingAdminRights
from entity.permissions import HasProducerRights, HasProducerWriteRights
from entity.views.production_sites.production_sites import ProductionSiteViewSet


class ProductionSitePermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            ProductionSiteViewSet,
            [
                (
                    ["list", "retrieve"],
                    [(HasProducerRights | HasDoubleCountingAdminRights)()],
                ),
                (
                    ["create", "update", "partial_update", "destroy"],
                    [HasProducerWriteRights()],
                ),
            ],
        )
