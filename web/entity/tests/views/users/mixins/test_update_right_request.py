from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from entity.views.users.mixins.update_right_request import UpdateRightsRequestsActionMixin


class UpdateRightsRequestsActionMixinTest(TestCase):
    def setUp(self):
        self.patched_send_mail = patch("entity.views.users.mixins.update_right_request.send_mail").start()
        self.patched_settings = patch("entity.views.users.mixins.update_right_request.settings").start()

    def tearDown(self):
        patch.stopall()

    def test_sends_notification_email(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = False
        self.patched_settings.DEFAULT_FROM_EMAIL = "from@example.com"
        self.patched_send_mail.assert_not_called()

        request = MagicMock()
        request.user.email = "user@example.com"

        UpdateRightsRequestsActionMixin.send_rights_update_notification(request)
        self.patched_send_mail.assert_called_with(
            request=request,
            subject="Carbure - Demande acceptée",
            message=ANY,
            from_email="from@example.com",
            recipient_list=["user@example.com"],
        )

    def test_decorates_notification_email_if_feature_flipped(self):
        self.patched_settings.WITH_EMAIL_DECORATED_AS_TEST = True
        self.patched_send_mail.assert_not_called()

        request = MagicMock()
        request.user.email = "user@example.com"

        UpdateRightsRequestsActionMixin.send_rights_update_notification(request)
        self.patched_send_mail.assert_called_with(
            request=ANY,
            subject=ANY,
            message=ANY,
            from_email=ANY,
            recipient_list=["carbure@beta.gouv.fr"],
        )
