from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from apikey.models import APIKey
from apikey.serializers import APIKeyListSerializer, APIKeySerializer


class APIKeyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return APIKey.objects.none()

        if self.request.user.is_anonymous:
            return APIKey.objects.none()

        return APIKey.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return APIKeyListSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["post"], detail=True)
    def revoke(self, request, id=None):
        apikey = self.get_object()

        if apikey.user != request.user:
            raise PermissionDenied({"message": "you do not have permission to revoke this apikey"})

        apikey.revoked = True
        apikey.save(update_fields=["revoked"])

        return Response({})
