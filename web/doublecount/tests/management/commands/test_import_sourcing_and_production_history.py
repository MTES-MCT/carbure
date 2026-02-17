from unittest import TestCase
from unittest.mock import MagicMock, patch

from doublecount.management.commands.import_sourcing_and_production_history import Command


class CommandTest(TestCase):
    def setUp(self):
        module_under_test = "doublecount.management.commands.import_sourcing_and_production_history"
        self.patched_log_exception = patch(f"{module_under_test}.log_exception").start()
        self.patched_private_storage = patch(f"{module_under_test}.private_storage").start()

    def tearDown(self):
        patch.stopall()

    def test_logs_error_to_Sentry_on_S3_upload_error(self):
        command = Command()
        command.stdout = MagicMock()
        self.patched_log_exception.assert_not_called()

        e = Exception("oops")
        self.patched_private_storage.save.side_effect = e
        s3_path = MagicMock()
        file = MagicMock()
        command.upload_dca_to_s3(s3_path, file)
        self.patched_log_exception.assert_called_with(e)
