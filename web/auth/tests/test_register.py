import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.test import APITestCase

from core.utils import CarbureEnv

User = get_user_model()


class RegisterTest(APITestCase):
    def setUp(self):
        self.url = reverse("auth-register")

    def test_responds_with_success_status(self):
        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "newuser@example.com",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": "success"}

    def test_sends_email(self):
        assert len(mail.outbox) == 0

        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "newuser@example.com",
        }
        self.client.post(self.url, data)
        assert len(mail.outbox) == 1

    def test_injects_server_base_url_in_sent_mail(self):
        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "newuser@example.com",
        }
        self.client.post(self.url, data)
        sent_mail = mail.outbox[0]
        assert re.search(CarbureEnv.get_base_url(), sent_mail.body)

    def test_does_not_precede_base_url_by_https(self):
        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "newuser@example.com",
        }
        self.client.post(self.url, data)
        sent_mail = mail.outbox[0]
        assert not re.search("https://http://", sent_mail.body)

    def test_sends_alternative_html_format(self):
        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "newuser@example.com",
        }
        self.client.post(self.url, data)
        sent_mail = mail.outbox[0]
        assert len(sent_mail.alternatives) == 1

        _, mimetype = sent_mail.alternatives[0]
        assert mimetype == "text/html"

    def test_does_not_precede_base_url_by_https_in_alternative_html_format(self):
        data = {
            "name": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "newuser@example.com",
        }
        self.client.post(self.url, data)
        sent_mail = mail.outbox[0]
        html_content, _ = sent_mail.alternatives[0]
        assert not re.search("https://http://", html_content)

    @patch("auth.serializers.UserCreationSerializer.is_valid")
    def test_responds_with_http_400_error_when_invalid_data(self, is_valid):
        is_valid.side_effect = ValidationError("oups")
        response = self.client.post(self.url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data[0] == "oups"
