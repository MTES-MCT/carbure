from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.digestate.spreading import (
    BiomethaneDigestateSpreadingAddSerializer,
)
from biomethane.utils import get_declaration_period


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class BiomethaneDigestateSpreadingViewSet(GenericViewSet, CreateModelMixin, DestroyModelMixin):
    queryset = BiomethaneDigestateSpreading.objects.all()
    serializer_class = BiomethaneDigestateSpreadingAddSerializer

    def get_permissions(self):
        get_biomethane_permissions(["create", "destroy"], self.action)

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        setattr(request, "year", get_declaration_period())
        return request

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["year"] = getattr(self.request, "year", None)
        return context
