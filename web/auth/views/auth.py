from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from auth.serializers import UserCreationSerializer

from .mixins import AuthActionMixin


class AuthViewSet(viewsets.ViewSet, AuthActionMixin):
    serializer_class = UserCreationSerializer  # default for schema
    permission_classes = []

    def get_permissions(self):
        if self.action in ["request_otp", "verify_otp"]:
            return [IsAuthenticated()]
        return super().get_permissions()
