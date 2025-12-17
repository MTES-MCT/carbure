from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from doublecount.permissions import HasDoubleCountingAdminRights, HasDoubleCountingAdminWriteRights, HasProducerRights
from doublecount.views.applications.application import ApplicationViewSet
from entity.permissions import HasProducerWriteRights


class DoubleCountingApplicationPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        self.assertViewPermissions(
            ApplicationViewSet,
            [
                (
                    ["retrieve", "filters"],
                    [(HasProducerRights | HasDoubleCountingAdminRights)()],
                ),
                (
                    ["check_file", "add", "upload_files", "delete_file"],
                    [HasProducerWriteRights()],
                ),
                (
                    ["list_admin", "export", "download_all_documents"],
                    [HasDoubleCountingAdminRights()],
                ),
                (
                    ["approve", "reject", "generate_decision", "update_approved_quotas"],
                    [HasDoubleCountingAdminWriteRights()],
                ),
            ],
        )
