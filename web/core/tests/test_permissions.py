from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import path, reverse
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carbure.urls import urlpatterns as carbure_urlpatterns
from core.permissions import IsVerified


class IsVerifiedView(APIView):
    permission_classes = [IsVerified]

    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    *carbure_urlpatterns,
    path("test/is-verified/", IsVerifiedView.as_view(), name="test-is-verified"),
]

test_middleware = list(settings.MIDDLEWARE)
authentication_middleware_index = test_middleware.index("django.contrib.auth.middleware.AuthenticationMiddleware")
test_middleware.insert(authentication_middleware_index + 1, "django_otp.middleware.OTPMiddleware")


@override_settings(ROOT_URLCONF=__name__, MIDDLEWARE=test_middleware)
class IsVerifiedIntegrationTest(TestCase):
    def setUp(self):
        self.password = "testpassword123"
        self.user = get_user_model().objects.create_user(
            name="testuser",
            email="testuser@example.com",
            password=self.password,
        )

    def login(self):
        credentials = {"username": self.user.email, "password": self.password}
        response = self.client.post(reverse("auth-login"), credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def verify_otp(self):
        response = self.client.get(reverse("auth-request-otp"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        device = EmailDevice.objects.get(user=self.user, name="email")
        response = self.client.post(reverse("auth-verify-otp"), {"otp_token": device.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def assert_verified(self, expected_code):
        response = self.client.get(reverse("test-is-verified"))
        self.assertEqual(response.status_code, expected_code)

    def test_denies_unauthenticated_request(self):
        self.assert_verified(status.HTTP_403_FORBIDDEN)

    def test_denies_unverified_user(self):
        self.login()
        self.assert_verified(status.HTTP_403_FORBIDDEN)

    def test_allows_verified_user(self):
        self.login()
        self.verify_otp()
        self.assert_verified(status.HTTP_204_NO_CONTENT)
