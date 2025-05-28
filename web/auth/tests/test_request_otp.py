import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework import status
from rest_framework.test import APIClient

from core.utils import CarbureEnv

User = get_user_model()


class RequestOTPTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.request_otp_url = reverse("auth-request-otp")

    def test_creates_email_device(self):
        self.client.force_authenticate(user=self.user)
        assert not EmailDevice.objects.filter(user=self.user).exists()

        self.client.get(self.request_otp_url)
        assert EmailDevice.objects.filter(user=self.user).exists()

    def test_responds_with_token_validity(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.request_otp_url)
        assert response.status_code == status.HTTP_200_OK
        assert "valid_until" in response.data
        assert response.data["valid_until"] is not None

    def test_sends_email(self):
        assert len(mail.outbox) == 0

        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        assert len(mail.outbox) == 1

    def test_injects_server_base_url_in_sent_mail(self):
        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        sent_mail = mail.outbox[0]
        assert re.search(CarbureEnv.get_base_url(), sent_mail.body)

    def test_does_not_precede_base_url_by_https(self):
        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        sent_mail = mail.outbox[0]
        assert not re.search("https://http://", sent_mail.body)

    def test_sends_alternative_html_format(self):
        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        sent_mail = mail.outbox[0]
        assert len(sent_mail.alternatives) == 1
        assert sent_mail.alternatives[0][1] == "text/html"

    def test_does_not_precede_base_url_by_https_in_alternative_html_format(self):
        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        sent_mail = mail.outbox[0]
        html_content = sent_mail.alternatives[0][0]
        assert not re.search("https://http://", html_content)

    def test_returns_http_403_if_user_not_authenticated(self):
        response = self.client.get(self.request_otp_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_does_not_create_email_device_if_user_not_authenticated(self):
        self.client.get(self.request_otp_url)
        assert not EmailDevice.objects.filter(user=self.user).exists()

    def test_does_not_send_email_if_user_not_authenticated(self):
        self.client.get(self.request_otp_url)
        assert len(mail.outbox) == 0
