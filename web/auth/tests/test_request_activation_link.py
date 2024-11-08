from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class RequestActivationLinkTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@example.com",
            password="testpassword123",
            is_active=False,
        )
        self.request_activation_link_url = reverse("auth-request-activation-link")

    def test_request_activation_link_success(self):
        data = {"email": self.user.email}
        response = self.client.post(self.request_activation_link_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": "success"}

    def test_request_activation_link_invalid_email(self):
        data = {"email": "invalid@example.com"}
        response = self.client.post(self.request_activation_link_url, data)
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in data
