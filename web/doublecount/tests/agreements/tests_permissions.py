from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from doublecount.permissions import HasDoubleCountingAdminRights, HasProducerRights
from doublecount.views.agreements.agreement import AgreementViewSet


class DoubleCountingApplicationPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            AgreementViewSet,
            [
                (
                    ["filters", "list", "retrieve"],
                    [(HasProducerRights | HasDoubleCountingAdminRights)()],
                ),
                (
                    ["export", "agreement_admin"],
                    [HasDoubleCountingAdminRights()],
                ),
                (
                    ["agreements_public_list"],
                    [],
                ),
            ],
        )
