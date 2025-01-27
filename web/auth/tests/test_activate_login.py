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
        "_auth_user_id" not in self.client.session
        data = {"uidb64": self.uidb64, "token": self.token, "invite": 0}
        response = self.client.post(self.active_url, data)
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.is_active
        assert "_auth_user_id" in self.client.session
        self.client.get(self.logout_url)
        assert "_auth_user_id" not in self.client.session

        login_data = {"username": "test@example.com", "password": "testpass"}
        login_response = self.client.post(self.login_url, login_data)
        data = login_response.json()

        assert login_response.status_code == status.HTTP_200_OK

        assert "_auth_user_id" in self.client.session

    def test_activate_and_login_account_invalid_token(self):
        assert "_auth_user_id" not in self.client.session
        data = {"uidb64": self.uidb64, "token": "invalidtoken", "invite": 0}
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
        data = {"uidb64": invalid_uidb64, "token": self.token, "invite": 0}
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

    @patch("django.contrib.auth.tokens.PasswordResetTokenGenerator.make_token")
    def test_activate_and_login_account_with_invite(self, mock_make_token):
        assert "_auth_user_id" not in self.client.session

        mock_token = "mockedpasstoken"
        mock_make_token.return_value = mock_token
        data = {"uidb64": self.uidb64, "token": self.token, "invite": 1}
        response = self.client.post(self.active_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"token": mock_token}
        self.user.refresh_from_db()
        assert self.user.is_active

        assert "_auth_user_id" in self.client.session

        self.client.get(self.logout_url)
        assert "_auth_user_id" not in self.client.session

        login_data = {"username": "test@example.com", "password": "testpass"}
        login_response = self.client.post(self.login_url, login_data)
        data = login_response.json()

        assert login_response.status_code == status.HTTP_200_OK

        assert "_auth_user_id" in self.client.session
