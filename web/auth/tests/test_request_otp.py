from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework import status
from rest_framework.test import APIClient

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

    def test_request_otp_creates_email_device_and_sends_token(self):
        self.client.force_authenticate(user=self.user)
        assert not EmailDevice.objects.filter(user=self.user).exists()

        response = self.client.get(self.request_otp_url)

        assert response.status_code == status.HTTP_200_OK

        assert EmailDevice.objects.filter(user=self.user).exists()

        assert "valid_until" in response.data
        assert response.data["valid_until"] is not None

    def test_sends_email(self):
        self.assertEqual(len(mail.outbox), 0)

        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        self.assertEqual(len(mail.outbox), 1)

    def test_injects_server_base_url_in_sent_mail(self):
        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        sent_mail = mail.outbox[0]
        self.assertRegex(sent_mail.body, "http://carbure.local:8090/")

    def test_does_not_precede_base_url_by_https(self):
        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        sent_mail = mail.outbox[0]
        self.assertNotRegex(sent_mail.body, "https://http://")

    def test_sends_alternative_html_format(self):
        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        sent_mail = mail.outbox[0]
        self.assertEqual(len(sent_mail.alternatives), 1)
        self.assertEqual(sent_mail.alternatives[0][1], 'text/html')

    def test_does_not_precede_base_url_by_https_in_alternative_html_format(self):
        self.client.force_authenticate(user=self.user)
        self.client.get(self.request_otp_url)
        sent_mail = mail.outbox[0]
        html_content = sent_mail.alternatives[0][0]
        self.assertNotRegex(html_content, "https://http://")

    def test_request_otp_creates_email_device_and_sends_token_not_auth(self):
        assert not EmailDevice.objects.filter(user=self.user).exists()

        response = self.client.get(self.request_otp_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert not EmailDevice.objects.filter(user=self.user).exists()
