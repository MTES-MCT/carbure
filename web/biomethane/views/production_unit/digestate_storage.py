from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import ModelViewSet

from biomethane.filters.mixins import EntityProducerFilter
from biomethane.models import BiomethaneDigestateStorage
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers import (
    BiomethaneDigestateStorageInputSerializer,
    BiomethaneDigestateStorageSerializer,
)


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

    def list(self, request, *args, **kwargs):
        # Apply filterset and check permissions on the first report
        queryset = self.filter_queryset(self.get_queryset())
        first_storage = queryset.first()
        if first_storage:
            self.check_object_permissions(request, first_storage)

        return super().list(request, *args, **kwargs)
