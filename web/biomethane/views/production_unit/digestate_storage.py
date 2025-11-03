from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import ModelViewSet

from biomethane.filters.mixins import EntityProducerFilter
from biomethane.models import BiomethaneDigestateStorage
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers import (
    BiomethaneDigestateStorageInputSerializer,
    BiomethaneDigestateStorageSerializer,
)
from biomethane.views.mixins import ListWithObjectPermissionsMixin


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
class BiomethaneDigestateStorageViewSet(ListWithObjectPermissionsMixin, ModelViewSet):
    queryset = BiomethaneDigestateStorage.objects.all()
    filterset_class = EntityProducerFilter
    serializer_class = BiomethaneDigestateStorageSerializer
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["create", "destroy", "destoy", "partial_update"], self.action)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BiomethaneDigestateStorageInputSerializer
        return BiomethaneDigestateStorageSerializer
