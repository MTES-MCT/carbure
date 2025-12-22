from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from entity.services.enable_depot import send_email_to_admin_users


class SendEmailToAdminUserTest(TestCase):
    def setUp(self):
        self.patched_send_mail = patch("entity.services.enable_depot.send_mail").start()
        self.patched_settings = patch("entity.services.enable_depot.settings").start()

    def tearDown(self):
        patch.stopall()

    def test_sends_email(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = False
        self.patched_settings.DEFAULT_FROM_EMAIL = "from@example.com"
        self.patched_send_mail.assert_not_called()

        entity = MagicMock()
        depot = MagicMock()
        depot.name = "NOM_DEPOT"
        admins = [MagicMock(**{"user.email": "admin@example.com"})]
        request = MagicMock()

        send_email_to_admin_users(entity, depot, admins, request)
        self.patched_send_mail.assert_called_with(
            request=request,
            subject="[CarbuRe][Votre demande de création du dépôt NOM_DEPOT a été acceptée]",
            message=ANY,
            from_email="from@example.com",
            recipient_list=["admin@example.com"],
        )

    def test_decorates_email_if_feature_flipped(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = True
        self.patched_send_mail.assert_not_called()

        entity = MagicMock()
        depot = MagicMock()
        depot.name = "NOM_DEPOT"
        admins = [MagicMock(**{"user.email": "admin@example.com"})]
        request = MagicMock()

        send_email_to_admin_users(entity, depot, admins, request)
        self.patched_send_mail.assert_called_with(
            request=ANY,
            subject="TEST [CarbuRe][Votre demande de création du dépôt NOM_DEPOT a été acceptée]",
            message=ANY,
            from_email=ANY,
            recipient_list=["carbure@beta.gouv.fr"],
        )
