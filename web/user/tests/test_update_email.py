from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.tests_utils import setup_current_user

User = get_user_model()


class UpdateEmailTest(TestCase):
    def setUp(self):
        self.user = setup_current_user(
            self,
            "test@carbure.local",
            "Test User",
            "testpassword123",
            [],
        )
        self.url = reverse("user-update-email")

    def test_update_email_success(self):
        data = {"new_email": "newemail@carbure.local", "password": "testpassword123"}

        response = self.client.put(self.url, data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "success"

        self.user.refresh_from_db()
        assert self.user.email == "newemail@carbure.local"

    def test_update_email_wrong_password(self):
        data = {"new_email": "newemail@carbure.local", "password": "wrongpassword"}

        response = self.client.put(self.url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.json()["errors"]

    def test_update_email_already_exists(self):
        User.objects.create_user(email="existing@carbure.local", password="password123")

        data = {"new_email": "existing@carbure.local", "password": "testpassword123"}

        response = self.client.put(self.url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_email" in response.json()["errors"]

    def test_update_email_invalid_format(self):
        data = {"new_email": "invalid-email", "password": "testpassword123"}

        response = self.client.put(self.url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_email" in response.json()["errors"]

    def test_update_email_missing_fields(self):
        data = {"new_email": "newemail@carbure.local"}

        response = self.client.put(self.url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.json()["errors"]

    def test_update_email_unauthenticated(self):
        self.client.logout()

        data = {"new_email": "newemail@carbure.local", "password": "testpassword123"}

        response = self.client.put(self.url, data, content_type="application/json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
