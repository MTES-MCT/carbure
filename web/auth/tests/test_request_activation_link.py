import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from auth.tokens import account_activation_token
from core.carburetypes import CarbureError
from core.models import Entity, UserRights

User = get_user_model()


class RequestActivationLinkTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.request_activation_link_url = reverse("auth-request-activation-link")
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@example.com",
            password="testpassword123",
            is_active=False,
        )

    def test_responds_with_success_status(self):
        response = self.client.post(self.request_activation_link_url, {"email": "testuser@example.com"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": "success"}

    def test_sends_email(self):
        assert len(mail.outbox) == 0

        self.client.post(self.request_activation_link_url, {"email": "testuser@example.com"})
        assert len(mail.outbox) == 1

    @patch.dict("os.environ", {"BASE_URL": "https://carbure.example.com"})
    def test_injects_server_base_url_in_sent_mail(self):
        self.client.post(self.request_activation_link_url, {"email": "testuser@example.com"})
        sent_mail = mail.outbox[0]
        assert re.search("https://carbure.example.com", sent_mail.body)

    def test_does_not_precede_base_url_by_https(self):
        self.client.post(self.request_activation_link_url, {"email": "testuser@example.com"})
        sent_mail = mail.outbox[0]
        assert not re.search("https://http://", sent_mail.body)

    def test_sends_alternative_html_format(self):
        self.client.post(self.request_activation_link_url, {"email": "testuser@example.com"})
        sent_mail = mail.outbox[0]
        assert len(sent_mail.alternatives) == 1
        _, mimetype = sent_mail.alternatives[0]
        assert mimetype == "text/html"

    def test_does_not_precede_base_url_by_https_in_alternative_html_format(self):
        self.client.post(self.request_activation_link_url, {"email": "testuser@example.com"})
        sent_mail = mail.outbox[0]
        html_content, _ = sent_mail.alternatives[0]
        assert not re.search("https://http://", html_content)

    @override_settings(PASSWORD_RESET_TIMEOUT=-1)
    def test_expired_signed_token_resends_to_the_account(self):
        token = account_activation_token.make_token(self.user)
        assert not account_activation_token.check_token(self.user, token)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.post(self.request_activation_link_url, {"uidb64": uidb64, "token": token})

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [self.user.email]

    def test_account_id_without_issued_token_sends_nothing(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.post(self.request_activation_link_url, {"uidb64": uidb64, "token": "not-issued"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.ACTIVATION_LINK_ERROR
        assert len(mail.outbox) == 0

    def test_unknown_account_id_sends_nothing(self):
        response = self.client.post(
            self.request_activation_link_url,
            {"uidb64": "not-an-account", "token": "not-issued"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.ACTIVATION_LINK_ERROR
        assert len(mail.outbox) == 0

    def test_link_of_an_activated_account_reports_already_active(self):
        token = account_activation_token.make_token(self.user)
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.post(self.request_activation_link_url, {"uidb64": uidb64, "token": token})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.ACCOUNT_ALREADY_ACTIVE
        assert len(mail.outbox) == 0

    def test_unrelated_token_of_an_activated_account_is_rejected(self):
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.post(self.request_activation_link_url, {"uidb64": uidb64, "token": "not-issued"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.ACTIVATION_LINK_ERROR
        assert len(mail.outbox) == 0

    def test_responds_with_http_200_on_request_with_unknown_email(self):
        response = self.client.post(self.request_activation_link_url, {"email": "unknown@example.com"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": "success"}

    def test_does_not_send_when_account_is_already_active(self):
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])

        response = self.client.post(self.request_activation_link_url, {"email": self.user.email})

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

    def test_resend_keeps_password_and_previous_link_for_registered_user(self):
        previous = account_activation_token.make_token(self.user)
        password = self.user.password

        self.client.post(self.request_activation_link_url, {"email": self.user.email})

        self.user.refresh_from_db()
        assert self.user.password == password
        assert account_activation_token.check_token(self.user, previous)
        assert "/auth/activate?" in mail.outbox[0].body

    def test_resend_invalidates_previous_link_for_invited_user(self):
        invited = User.objects.create_user(email="invited@example.com", password=None, is_active=False)
        Entity.objects.create(name="Entité invitante")
        UserRights.objects.create(
            user=invited,
            entity=Entity.objects.get(name="Entité invitante"),
            role=UserRights.RO,
        )
        previous = account_activation_token.make_token(invited)

        response = self.client.post(self.request_activation_link_url, {"email": invited.email})

        assert response.status_code == status.HTTP_200_OK
        invited.refresh_from_db()
        assert not invited.has_usable_password()
        assert not account_activation_token.check_token(invited, previous)
        body = mail.outbox[0].body
        assert "/auth/join?" in body
        assert "Entité invitante" in body
        token = re.search(r"token=([^&\s]+)", body).group(1)
        assert account_activation_token.check_token(invited, token)
