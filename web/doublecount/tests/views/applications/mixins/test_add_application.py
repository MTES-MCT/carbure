from unittest import TestCase
from unittest.mock import MagicMock, patch

from doublecount.views.applications.mixins.add_application import AddActionMixin


class AddActionMixinTest(TestCase):
    def setUp(self):
        self.patched_log_exception = patch("doublecount.views.applications.mixins.add_application.log_exception").start()
        self.patched_private_storage = patch("doublecount.views.applications.mixins.add_application.private_storage").start()

    def tearDown(self):
        patch.stopall()

    def test_logs_errors_to_Sentry_on_S3_error(self):
        mixin = AddActionMixin()
        self.patched_log_exception.assert_not_called()

        s3_path = MagicMock()
        file = MagicMock()
        dca = MagicMock()
        extra_files = MagicMock()
        e = Exception("oops")
        self.patched_private_storage.save.side_effect = e
        mixin.upload_file_to_s3(s3_path, file, dca, extra_files)
        self.patched_log_exception.assert_called_with(e)
