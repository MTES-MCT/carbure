from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import ModelViewSet

from biomethane.models import BiomethaneDigestateStorage
from biomethane.serializers.digestate_storage import (
    BiomethaneDigestateStorageAddSerializer,
    BiomethaneDigestateStoragePatchSerializer,
    BiomethaneDigestateStorageSerializer,
)
from core.models import Entity, UserRights
from core.permissions import HasUserRights


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class BiomethaneDigestateStorageViewSet(ModelViewSet):
    serializer_class = BiomethaneDigestateStorageSerializer
    permission_classes = [HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_permissions(self):
        if self.action in [
            "create",
            "destroy",
            "update",
            "partial_update",
        ]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return BiomethaneDigestateStorage.objects.none()
        return BiomethaneDigestateStorage.objects.filter(producer=self.request.entity)

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneDigestateStorageAddSerializer
        elif self.action in ["update", "partial_update"]:
            return BiomethaneDigestateStoragePatchSerializer
        return BiomethaneDigestateStorageSerializer
