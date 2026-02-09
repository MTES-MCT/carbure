from unittest import TestCase
from unittest.mock import MagicMock, patch

from doublecount.helpers import check_dc_file, send_dca_confirmation_email


class SendDCAConfirmationEmailTest(TestCase):
    def setUp(self):
        self.patched_log_exception = patch("doublecount.helpers.log_exception").start()
        self.patched_load_dc_filepath = patch("doublecount.helpers.load_dc_filepath").start()
        self.patched_parse_dc_excel = patch("doublecount.helpers.parse_dc_excel").start()
        self.patched_send_mail = patch("doublecount.helpers.send_mail").start()
        self.patched_UserRights = patch("doublecount.helpers.UserRights").start()

    def tearDown(self):
        patch.stopall()

    def test_logs_errors_to_Sentry_on_email_sending_error(self):
        self.patched_log_exception.assert_not_called()

        e = Exception("oops")
        self.patched_send_mail.side_effect = e
        dca = MagicMock()
        request = MagicMock()
        send_dca_confirmation_email(dca, request)
        self.patched_log_exception.assert_called_with(e)

    def test_logs_errors_to_Sentry_on_Excel_parsing_error(self):
        self.patched_log_exception.assert_not_called()

        e = Exception("oops")
        self.patched_parse_dc_excel.side_effect = e
        file = MagicMock()
        check_dc_file(file)
        self.patched_log_exception.assert_called_with(e)
