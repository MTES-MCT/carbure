from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from core.carburetypes import CarbureError

User = get_user_model()


class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.request_password_reset_url = reverse("auth-request-password-reset")
        self.reset_password_url = reverse("auth-reset-password")

    @patch("auth.views.mixins.request_password_reset.send_mail")
    def test_request_password_reset_success(self, mock_send_mail):
        mock_send_mail.return_value = 1

        data = {"username": self.user.email}
        response = self.client.post(self.request_password_reset_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": "success"}

        assert mock_send_mail.called
        assert mock_send_mail.call_count == 1

        email_context = mock_send_mail.call_args[1]
        assert "uid" in email_context["html_message"]
        assert "token" in email_context["html_message"]
        assert self.user.email in email_context["recipient_list"]

    def test_request_password_reset_user_not_found(self):
        data = {"username": "nonexistent@example.com"}
        response = self.client.post(self.request_password_reset_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.PASSWORD_RESET_USER_NOT_FOUND

    def test_reset_password_success(self):
        prtg = PasswordResetTokenGenerator()
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = prtg.make_token(self.user)

        new_password = "newpassword123"
        data = {
            "uidb64": uidb64,
            "token": token,
            "password1": new_password,
            "password2": new_password,
        }
        response = self.client.post(self.reset_password_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": "success"}

        self.user.refresh_from_db()
        assert self.user.check_password(new_password)

    def test_reset_password_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        invalid_token = "invalid-token"

        data = {
            "uidb64": uidb64,
            "token": invalid_token,
            "password1": "newpassword123",
            "password2": "newpassword123",
        }
        response = self.client.post(self.reset_password_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.PASSWORD_RESET_INVALID_FORM
