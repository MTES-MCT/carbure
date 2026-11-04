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
        assert response.data == {}
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

    def test_activate_rejects_an_invited_account_that_has_no_password(self):
        invited_user, uidb64, token = self.invited_account()
        response = self.client.post(self.active_url, {"uidb64": uidb64, "token": token})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER
        invited_user.refresh_from_db()
        assert not invited_user.is_active
        assert not invited_user.has_usable_password()
        assert account_activation_token.check_token(invited_user, token)

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

    def test_check_activate_profile_accepts_a_valid_link_without_changing_the_account(self):
        invited_user, uidb64, token = self.invited_account()

        response = self.client.post(reverse("auth-check-activate-profile"), {"uidb64": uidb64, "token": token})

        assert response.status_code == status.HTTP_200_OK
        invited_user.refresh_from_db()
        assert not invited_user.is_active
        assert not invited_user.has_usable_password()
        assert account_activation_token.check_token(invited_user, token)

    def test_check_activate_profile_rejects_an_expired_link(self):
        invited_user, uidb64, _token = self.invited_account()
        issued_at = account_activation_token._num_seconds(account_activation_token._now())
        expired = account_activation_token._make_token_with_timestamp(
            invited_user,
            issued_at - 60 * 60 - 1,
            account_activation_token.secret,
        )

        response = self.client.post(reverse("auth-check-activate-profile"), {"uidb64": uidb64, "token": expired})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER
        invited_user.refresh_from_db()
        assert not invited_user.is_active

    def test_activate_profile_sets_name_password_and_activates(self):
        invited_user, uidb64, token = self.invited_account()
        profile_url = reverse("auth-activate-profile")

        response = self.client.post(
            profile_url,
            {
                "uidb64": uidb64,
                "token": token,
                "name": "Camille Bernard",
                "password1": "UnePhraseAssezLongue",
                "password2": "UnePhraseAssezLongue",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        invited_user.refresh_from_db()
        assert invited_user.is_active
        assert invited_user.name == "Camille Bernard"
        assert invited_user.check_password("UnePhraseAssezLongue")
        assert not account_activation_token.check_token(invited_user, token)
        assert "_auth_user_id" not in self.client.session

    def test_activate_profile_rejects_a_weak_password_without_consuming_the_link(self):
        invited_user, uidb64, token = self.invited_account()

        response = self.client.post(
            reverse("auth-activate-profile"),
            {
                "uidb64": uidb64,
                "token": token,
                "name": "Camille Bernard",
                "password1": "password",
                "password2": "password",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        invited_user.refresh_from_db()
        assert not invited_user.is_active
        assert invited_user.name != "Camille Bernard"
        assert account_activation_token.check_token(invited_user, token)

    def test_activate_profile_rejects_a_too_long_name_without_consuming_the_link(self):
        invited_user, uidb64, token = self.invited_account()

        response = self.client.post(
            reverse("auth-activate-profile"),
            {
                "uidb64": uidb64,
                "token": token,
                "name": "A" * 256,
                "password1": "UnePhraseAssezLongue",
                "password2": "UnePhraseAssezLongue",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
        invited_user.refresh_from_db()
        assert not invited_user.is_active
        assert account_activation_token.check_token(invited_user, token)

    def test_activate_profile_hides_field_errors_when_the_link_is_invalid(self):
        invited_user, uidb64, _token = self.invited_account()

        response = self.client.post(
            reverse("auth-activate-profile"),
            {
                "uidb64": uidb64,
                "token": "not-issued",
                "name": "Camille Bernard",
                "password1": "UnePhraseAssezLongue",
                "password2": "different-phrase",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER
        assert "password2" not in response.data
        invited_user.refresh_from_db()
        assert not invited_user.is_active

    def test_activate_profile_rejects_an_account_that_already_has_a_password(self):
        response = self.client.post(
            reverse("auth-activate-profile"),
            {
                "uidb64": self.uidb64,
                "token": self.token,
                "name": "Autre Nom",
                "password1": "UnePhraseAssezLongue",
                "password2": "UnePhraseAssezLongue",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.user.refresh_from_db()
        assert not self.user.is_active
        assert self.user.name == "testuser"
        assert self.user.check_password("testpass")

    def invited_account(self):
        invited_user = User.objects.create_user(email="invited@example.com", password=None, is_active=False)
        uidb64 = urlsafe_base64_encode(force_bytes(invited_user.pk))
        token = account_activation_token.make_token(invited_user)
        return invited_user, uidb64, token
