from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class ChangeEmailTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="testpassword123")
        self.client.force_authenticate(user=self.user)

    def test_request_email_change_success(self):
        data = {"new_email": "newemail@example.com", "password": "testpassword123"}
        url = reverse("auth-request-email-change")
        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "otp_sent"

        device = EmailDevice.objects.filter(
            user=self.user, name__startswith="email_change_", email="newemail@example.com"
        ).first()
        assert device is not None
        assert device.confirmed is False

    def test_request_email_change_wrong_password(self):
        data = {"new_email": "newemail@example.com", "password": "wrongpassword"}
        url = reverse("auth-request-email-change")

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_request_email_change_existing_email(self):
        User.objects.create_user(email="existing@example.com", password="password123")

        data = {"new_email": "existing@example.com", "password": "testpassword123"}
        url = reverse("auth-request-email-change")

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_email_change_success(self):
        new_email = "newemail@example.com"

        # Simulate step 1: Request email change
        device = EmailDevice()
        device.user = self.user
        device.name = f"email_change_{new_email}"
        device.email = new_email
        device.confirmed = False
        device.save()
        device.generate_token()

        data = {"new_email": new_email, "otp_token": device.token}
        url = reverse("auth-confirm-email-change")

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"

        self.user.refresh_from_db()
        assert self.user.email == new_email

        assert not EmailDevice.objects.filter(user=self.user, name=f"email_change_{new_email}").exists()

    def test_confirm_email_change_wrong_token(self):
        new_email = "newemail@example.com"

        # Simulate step 1: Request email change
        device = EmailDevice()
        device.user = self.user
        device.name = f"email_change_{new_email}"
        device.email = new_email
        device.confirmed = False
        device.save()
        device.generate_token()

        data = {
            "new_email": new_email,
            "otp_token": "123456",  # Mauvais token
        }
        url = reverse("auth-confirm-email-change")

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.user.refresh_from_db()
        assert self.user.email == "test@example.com"

    def test_confirm_email_change_no_request(self):
        data = {"new_email": "newemail@example.com", "otp_token": "123456"}
        url = reverse("auth-confirm-email-change")

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
