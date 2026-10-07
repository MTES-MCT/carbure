from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from doublecount.permissions import (
    HasDoubleCountingAdminRights,
    HasDoubleCountingAdminWriteRights,
    HasProducerRights,
)
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
                    ["update_status", "bulk_update_status"],
                    [HasDoubleCountingAdminWriteRights()],
                ),
                (
                    ["agreements_public_list"],
                    [],
                ),
            ],
        )
