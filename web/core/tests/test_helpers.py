from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser

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
        request.user.is_authenticated = True
        request.user.email = "other@example.com"
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

    def test_decorates_email_and_keeps_recipient_when_authenticated_user_is_in_list(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = True
        self.patched_EmailMultiAlternatives.assert_not_called()

        request = MagicMock()
        request.user.is_authenticated = True
        request.user.email = "user@example.com"
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
            ["user@example.com"],
            cc=None,
        )

    def test_decorates_email_and_keeps_recipient_during_registration(self):
        """Unauthenticated requests (e.g. registration) must keep the original recipient."""
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = True
        self.patched_EmailMultiAlternatives.assert_not_called()

        request = MagicMock()
        request.user = AnonymousUser()
        send_mail(
            request=request,
            subject="A subject",
            message="A message",
            from_email="carbure@example.com",
            recipient_list=["newuser@example.com"],
            cc="additional_recipient@example.com",
        )

        self.patched_EmailMultiAlternatives.assert_called_with(
            "[TEST] A subject",
            "A message \n\n ['newuser@example.com']",
            "carbure@example.com",
            ["newuser@example.com"],
            cc=None,
        )

    def test_prepare_email_to_be_sent_without_request(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = False
        self.patched_EmailMultiAlternatives.assert_not_called()

        send_mail(
            request=None,
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

    def test_decorates_email_when_sending_without_request(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = True
        self.patched_EmailMultiAlternatives.assert_not_called()

        send_mail(
            request=None,
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
