from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from auth.views.auth import AuthViewSet


class AuthThrottlingTest(TestCase):
    def setUp(self):
        self.throttle_classes_patcher = patch.object(AuthViewSet, "throttle_classes", [ScopedRateThrottle])
        self.throttle_rates_patcher = patch.object(ScopedRateThrottle, "THROTTLE_RATES", {"10/day": "2/minute"})
        self.throttle_classes_patcher.start()
        self.throttle_rates_patcher.start()
        self.addCleanup(self.throttle_classes_patcher.stop)
        self.addCleanup(self.throttle_rates_patcher.stop)
        cache.clear()
        self.client = APIClient()

    def test_throttle_scope_is_set_for_each_throttled_action(self):
        throttled_actions = [
            "register",
            "request_otp",
            "request_activation_link",
            "verify_otp",
            "request_password_reset",
        ]

        for action in throttled_actions:
            with self.subTest(action=action):
                view = AuthViewSet()
                view.action = action

                throttles = view.get_throttles()

                self.assertEqual(view.throttle_scope, "10/day")
                self.assertEqual(len(throttles), 1)
                self.assertIsInstance(throttles[0], ScopedRateThrottle)

    def test_throttled_action_returns_429_after_rate_is_exceeded(self):
        url = reverse("auth-request-activation-link")
        data = {"email": "unknown@example.com"}

        self.assertEqual(self.client.post(url, data).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(url, data).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(url, data).status_code, status.HTTP_429_TOO_MANY_REQUESTS)
