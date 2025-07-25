import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.carburetypes import CarbureError
from core.utils import CarbureEnv

User = get_user_model()


class RequestPasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.request_password_reset_url = reverse("auth-request-password-reset")

    def test_responds_with_success_status_when_user_known(self):
        response = self.client.post(self.request_password_reset_url, {"username": "testuser@example.com"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": "success"}

    def test_sends_email_to_user(self):
        assert len(mail.outbox) == 0

        self.client.post(self.request_password_reset_url, {"username": "testuser@example.com"})
        assert len(mail.outbox) == 1
        assert "testuser@example.com" in mail.outbox[0].recipients()

    def test_uses_proper_mail_template(self):
        self.client.post(self.request_password_reset_url, {"username": "testuser@example.com"})
        assert "Réinitialisation du mot de passe" in mail.outbox[0].subject

    def test_injects_server_base_url_in_sent_mail(self):
        self.client.post(self.request_password_reset_url, {"username": "testuser@example.com"})
        sent_mail = mail.outbox[0]
        assert re.search(CarbureEnv.get_base_url(), sent_mail.body)

    def test_does_not_precede_base_url_by_https(self):
        self.client.post(self.request_password_reset_url, {"username": "testuser@example.com"})
        sent_mail = mail.outbox[0]
        assert not re.search("https://http://", sent_mail.body)

    def test_sends_alternative_html_format(self):
        self.client.post(self.request_password_reset_url, {"username": "testuser@example.com"})
        sent_mail = mail.outbox[0]
        assert len(sent_mail.alternatives) == 1

        _, mimetype = sent_mail.alternatives[0]
        assert mimetype == "text/html"

    def test_does_not_precede_base_url_by_https_in_alternative_html_format(self):
        self.client.post(self.request_password_reset_url, {"username": "testuser@example.com"})
        sent_mail = mail.outbox[0]
        html_content, _ = sent_mail.alternatives[0]
        assert not re.search("https://http://", html_content)

    def test_responds_with_http_400_error_when_user_unknown(self):
        response = self.client.post(self.request_password_reset_url, {"username": "unknown@example.com"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.PASSWORD_RESET_USER_NOT_FOUND
