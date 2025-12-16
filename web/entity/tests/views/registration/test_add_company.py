from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from entity.views.registration.add_company import send_email_to_user


class SendEmailToUserTest(TestCase):
    def setUp(self):
        self.patched_send_mail = patch("entity.views.registration.add_company.send_mail").start()
        self.patched_settings = patch("entity.views.registration.add_company.settings").start()

    def tearDown(self):
        patch.stopall()

    def test_sends_email(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = False
        self.patched_settings.DEFAULT_FROM_EMAIL = "from@example.com"
        self.patched_send_mail.assert_not_called()

        entity = MagicMock()
        entity.name = "Some Entity"
        request = MagicMock()
        request.user.email = "user@example.com"

        send_email_to_user(entity, request)
        self.patched_send_mail.assert_called_with(
            request=request,
            subject="Demande d'inscription de société enregistrée",
            message=ANY,
            from_email="from@example.com",
            recipient_list=["user@example.com"],
        )

    def test_decorates_email_if_feature_flipped(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = True
        self.patched_send_mail.assert_not_called()

        entity = MagicMock()
        request = MagicMock()
        request.user.email = "user@example.com"

        send_email_to_user(entity, request)
        self.patched_send_mail.assert_called_with(
            request=ANY,
            subject="TEST Demande d'inscription de société enregistrée",
            message=ANY,
            from_email=ANY,
            recipient_list=["carbure@beta.gouv.fr"],
        )
