from unittest import TestCase
from unittest.mock import MagicMock, patch

from core.helpers import send_mail


class SendMailTest(TestCase):
    def setUp(self):
        self.patched_EmailMultiAlternatives = patch("core.helpers.EmailMultiAlternatives").start()
        self.patched_settings = patch("core.helpers.settings").start()

    def tearDown(self):
        patch.stopall()

    def test_prepares_email_to_be_sent(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = False
        self.patched_EmailMultiAlternatives.assert_not_called()

        request = MagicMock()
        send_mail(
            request=request,
            subject="A subject",
            message="A message",
            from_email="carbure@example.com",
            recipient_list=["user@example.com"],
            cc="additional_recipient@example.com",
        )

        self.patched_EmailMultiAlternatives.assert_called_with(
            "A subject",
            "A message",
            "carbure@example.com",
            ["user@example.com"],
            cc="additional_recipient@example.com",
        )

    def test_decorates_email_if_feature_flipped(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = True
        self.patched_EmailMultiAlternatives.assert_not_called()

        request = MagicMock()
        send_mail(
            request=request,
            subject="A subject",
            message="A message",
            from_email="carbure@example.com",
            recipient_list=["user@example.com"],
            cc="additional_recipient@example.com",
        )

        self.patched_EmailMultiAlternatives.assert_called_with(
            "[TEST] A subject",
            "A message \n\n ['user@example.com']",
            "carbure@example.com",
            ["carbure@beta.gouv.fr"],
            cc=None,
        )
