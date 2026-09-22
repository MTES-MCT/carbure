from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from auth.serializers import UserCreationSerializer
from core.permissions import IsVerified

from .mixins import AuthActionMixin


def admin_login_redirect(request):
    return redirect("/auth/login/", permanent=True)


class AuthViewSet(viewsets.ViewSet, AuthActionMixin):
    serializer_class = UserCreationSerializer  # default for schema
    permission_classes = []
    # Declared so @action(throttle_scope=...) is accepted by ViewSet.as_view().
    throttle_scope = None

    def get_permissions(self):
        if self.action in ["request_otp", "verify_otp"]:
            return [IsAuthenticated()]
        if self.action in ["request_email_change", "confirm_email_change", "change_password"]:
            return [IsVerified()]
        return super().get_permissions()
