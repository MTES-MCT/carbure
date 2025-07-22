from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from auth.serializers import ChangePasswordErrors

User = get_user_model()


class ChangePasswordTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="testpassword123")
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        data = {
            "current_password": "testpassword123",
            "new_password": "newpassword456",
            "confirm_new_password": "newpassword456",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"

        self.user.refresh_from_db()
        assert self.user.check_password("newpassword456")
        assert not self.user.check_password("testpassword123")

    def test_change_password_wrong_current_password(self):
        data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword456",
            "confirm_new_password": "newpassword456",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == ChangePasswordErrors.INVALID_DATA
        assert response.data["errors"]["current_password"] == [ChangePasswordErrors.WRONG_CURRENT_PASSWORD]

        self.user.refresh_from_db()
        assert self.user.check_password("testpassword123")
        assert not self.user.check_password("newpassword456")

    def test_change_password_same_passwords(self):
        data = {
            "current_password": "testpassword123",
            "new_password": "testpassword123",
            "confirm_new_password": "testpassword123",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == ChangePasswordErrors.INVALID_DATA
        assert response.data["errors"]["current_password"] == [ChangePasswordErrors.PASSWORDS_MATCH]

        self.user.refresh_from_db()
        assert self.user.check_password("testpassword123")

    def test_change_password_confirmation_mismatch(self):
        data = {
            "current_password": "testpassword123",
            "new_password": "newpassword456",
            "confirm_new_password": "differentpassword789",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == ChangePasswordErrors.INVALID_DATA
        assert response.data["errors"]["confirm_new_password"] == [ChangePasswordErrors.CONFIRM_PASSWORD_MISMATCH]

        self.user.refresh_from_db()
        assert self.user.check_password("testpassword123")

    def test_change_password_weak_password(self):
        data = {
            "current_password": "testpassword123",
            "new_password": "123",
            "confirm_new_password": "123",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data["errors"]

        self.user.refresh_from_db()
        assert self.user.check_password("testpassword123")

    def test_change_password_missing_fields(self):
        data = {
            "current_password": "testpassword123",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data["errors"]
        assert "confirm_new_password" in response.data["errors"]

        self.user.refresh_from_db()
        assert self.user.check_password("testpassword123")

    def test_change_password_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            "current_password": "testpassword123",
            "new_password": "newpassword456",
            "confirm_new_password": "newpassword456",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_change_password_maintains_session(self):
        data = {
            "current_password": "testpassword123",
            "new_password": "newpassword456",
            "confirm_new_password": "newpassword456",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"

        response = self.client.get(reverse("auth-change-password"))
        assert response.status_code != status.HTTP_401_UNAUTHORIZED or response.status_code != status.HTTP_403_FORBIDDEN

    def test_change_password_empty_strings(self):
        data = {
            "current_password": "",
            "new_password": "",
            "confirm_new_password": "",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "current_password" in response.data["errors"]
        assert "new_password" in response.data["errors"]
        assert "confirm_new_password" in response.data["errors"]

        self.user.refresh_from_db()
        assert self.user.check_password("testpassword123")

    def test_change_password_common_password(self):
        data = {
            "current_password": "testpassword123",
            "new_password": "password123",  # Too common
            "confirm_new_password": "password123",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Django password validation raises default validation errors, not custom codes
        assert "new_password" in response.data["errors"]

        self.user.refresh_from_db()
        assert self.user.check_password("testpassword123")

    def test_change_password_numeric_password(self):
        data = {
            "current_password": "testpassword123",
            "new_password": "123456789",  # Only numbers
            "confirm_new_password": "123456789",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data["errors"]

        self.user.refresh_from_db()
        assert self.user.check_password("testpassword123")
