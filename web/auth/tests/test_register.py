from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTest(APITestCase):
    def setUp(self):
        self.url = reverse("auth-register")

    def test_register_success(self):
        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "newuser@example.com",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": "success"}

        user = User.objects.get(email="newuser@example.com")
        assert not user.is_active

    def test_register_password_mismatch(self):
        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "differentpassword",
            "email": "newuser@example.com",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password2" in response.data
        assert response.data["password2"][0] == "The two password fields didn't match."

    def test_register_email_exists(self):
        User.objects.create(name="newuser", email="existing@example.com")
        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "existing@example.com",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
