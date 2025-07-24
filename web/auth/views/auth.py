from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from auth.serializers import UserCreationSerializer

from .mixins import AuthActionMixin


class AuthViewSet(viewsets.ViewSet, AuthActionMixin):
    serializer_class = UserCreationSerializer  # default for schema
    permission_classes = []

    def get_permissions(self):
        if self.action in ["request_otp", "verify_otp", "request_email_change", "confirm_email_change", "change_password"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_throttles(self):
        if self.action in [
            "register",
            "request_otp",
            "request-activation-link",
            "verify-otp",
            "request-password-reset",
        ]:
            self.throttle_scope = "10/day"
        else:
            self.throttle_scope = None

        return super().get_throttles()
