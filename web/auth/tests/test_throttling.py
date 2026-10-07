from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from auth.views.auth import AuthViewSet

User = get_user_model()

THROTTLE_RATES = {"otp": "2/minute", "auth-anon": "2/minute", "add-company": "2/minute"}


class AuthThrottlingTest(TestCase):
    def setUp(self):
        self.throttle_classes_patcher = patch.object(AuthViewSet, "throttle_classes", [ScopedRateThrottle])
        self.throttle_rates_patcher = patch.object(ScopedRateThrottle, "THROTTLE_RATES", THROTTLE_RATES)
        self.throttle_classes_patcher.start()
        self.throttle_rates_patcher.start()
        self.addCleanup(self.throttle_classes_patcher.stop)
        self.addCleanup(self.throttle_rates_patcher.stop)
        cache.clear()
        self.client = APIClient()

    def test_throttle_scope_is_set_for_each_throttled_action(self):
        expected_scopes = {
            "register": "auth-anon",
            "activate": "auth-anon",
            "request_activation_link": "auth-anon",
            "request_password_reset": "auth-anon",
            "reset_password": "auth-anon",
            "request_otp": "otp",
            "verify_otp": "otp",
        }

        for action, expected_scope in expected_scopes.items():
            with self.subTest(action=action):
                self.assertEqual(getattr(AuthViewSet, action).kwargs["throttle_scope"], expected_scope)

    def test_unthrottled_action_has_no_scope(self):
        self.assertNotIn("throttle_scope", AuthViewSet.change_password.kwargs)

    def test_anon_action_returns_429_after_rate_is_exceeded(self):
        url = reverse("auth-request-activation-link")
        data = {"email": "unknown@example.com"}

        self.assertEqual(self.client.post(url, data).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(url, data).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(url, data).status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_anonymous_auth_endpoints_share_the_same_bucket(self):
        activation_url = reverse("auth-request-activation-link")
        reset_url = reverse("auth-request-password-reset")
        data = {"email": "unknown@example.com"}

        self.assertEqual(self.client.post(activation_url, data).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(activation_url, data).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(reset_url, data).status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_otp_bucket_is_isolated_from_anonymous_auth(self):
        user = User.objects.create_user(email="otp@example.com", password="testpassword123")
        activation_url = reverse("auth-request-activation-link")
        data = {"email": "unknown@example.com"}

        self.assertEqual(self.client.post(activation_url, data).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(activation_url, data).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(activation_url, data).status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("auth-request-otp"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_otp_action_returns_429_after_rate_is_exceeded(self):
        user = User.objects.create_user(email="otp-limit@example.com", password="testpassword123")
        self.client.force_authenticate(user=user)
        url = reverse("auth-request-otp")

        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_429_TOO_MANY_REQUESTS)
