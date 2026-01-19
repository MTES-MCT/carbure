from unittest import TestCase
from unittest.mock import MagicMock, patch

from doublecount.helpers import send_dca_confirmation_email


class SendDCAConfirmationEmailTest(TestCase):
    def setUp(self):
        self.patched_log_exception = patch("doublecount.helpers.log_exception").start()
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
