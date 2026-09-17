from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from auth.tokens import account_activation_token
from core.carburetypes import CarbureError

User = get_user_model()


class ActivateLoginAccountTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="testuser",
            email="test@example.com",
            password="testpass",
            is_active=False,
        )
        self.token = account_activation_token.make_token(self.user)

        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.active_url = reverse("auth-activate")
        self.login_url = reverse("auth-login")
        self.logout_url = reverse("auth-logout")

    def test_activate_and_login_account_success(self):
        """Activate a user account without auto-login, then allow explicit credential login."""
        "_auth_user_id" not in self.client.session
        data = {"uidb64": self.uidb64, "token": self.token}
        response = self.client.post(self.active_url, data)
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.is_active
        assert "_auth_user_id" not in self.client.session

        login_data = {"username": "test@example.com", "password": "testpass"}
        login_response = self.client.post(self.login_url, login_data)
        data = login_response.json()

        assert login_response.status_code == status.HTTP_200_OK

        assert "_auth_user_id" in self.client.session

    def test_activate_and_login_account_invalid_token(self):
        assert "_auth_user_id" not in self.client.session
        data = {"uidb64": self.uidb64, "token": "invalidtoken"}
        response = self.client.post(self.active_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.user.refresh_from_db()
        assert not self.user.is_active
        assert "message" in response.data
        assert response.data["message"] == CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER
        assert "_auth_user_id" not in self.client.session

        login_data = {"username": "test@example.com", "password": "testpass"}
        login_response = self.client.post(self.login_url, login_data)
        data = login_response.json()

        assert login_response.status_code == status.HTTP_400_BAD_REQUEST

        assert "_auth_user_id" not in self.client.session

    def test_activate_and_login_account_user_not_found(self):
        assert "_auth_user_id" not in self.client.session
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(9999))
        data = {"uidb64": invalid_uidb64, "token": self.token}
        response = self.client.post(self.active_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "message" in response.data
        assert response.data["message"] == CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER
        assert "_auth_user_id" not in self.client.session

        login_data = {"username": "test@example.com", "password": "testpass"}
        login_response = self.client.post(self.login_url, login_data)
        data = login_response.json()

        assert login_response.status_code == status.HTTP_400_BAD_REQUEST

        assert "_auth_user_id" not in self.client.session

    @patch("auth.tokens.password_reset_token.make_token")
    def test_activate_does_not_issue_reset_token_for_regular_user(self, mock_make_token):
        """Ignore client invite flag for regular profiles and never mint a reset token."""
        assert "_auth_user_id" not in self.client.session

        data = {"uidb64": self.uidb64, "token": self.token}
        response = self.client.post(self.active_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {}
        mock_make_token.assert_not_called()
        self.user.refresh_from_db()
        assert self.user.is_active
        assert "_auth_user_id" not in self.client.session

        login_data = {"username": "test@example.com", "password": "testpass"}
        login_response = self.client.post(self.login_url, login_data)
        data = login_response.json()

        assert login_response.status_code == status.HTTP_200_OK

        assert "_auth_user_id" in self.client.session

    def test_activation_token_cannot_be_reused(self):
        """Reject replay of the same activation token after first successful activation."""
        assert "_auth_user_id" not in self.client.session

        data = {"uidb64": self.uidb64, "token": self.token}
        first_response = self.client.post(self.active_url, data)
        assert first_response.status_code == status.HTTP_200_OK
        assert "_auth_user_id" not in self.client.session

        second_response = self.client.post(self.active_url, data)
        assert second_response.status_code == status.HTTP_400_BAD_REQUEST
        assert second_response.data["message"] == CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER
        assert "_auth_user_id" not in self.client.session

    def test_activate_issues_reset_token_for_invited_user_profile(self):
        """Issue a password-reset token for invited profiles based on server-side account state."""
        invited_user = User.objects.create_user(
            name="",
            email="invited@example.com",
            password="temporary-password",
            is_active=False,
        )
        invited_uidb64 = urlsafe_base64_encode(force_bytes(invited_user.pk))
        invited_token = account_activation_token.make_token(invited_user)

        with patch("auth.tokens.password_reset_token.make_token") as mock_make_token:
            mock_make_token.return_value = "mockedpasstoken"

            response = self.client.post(
                self.active_url,
                {"uidb64": invited_uidb64, "token": invited_token},
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"token": "mockedpasstoken"}
        invited_user.refresh_from_db()
        assert invited_user.is_active
        assert "_auth_user_id" not in self.client.session
