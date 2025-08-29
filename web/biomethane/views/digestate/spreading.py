from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading
from biomethane.serializers.digestate.spreading import (
    BiomethaneDigestateSpreadingAddSerializer,
)
from biomethane.utils import get_declaration_period
from core.models import Entity, UserRights
from core.permissions import HasUserRights


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
    permission_classes = [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        setattr(request, "year", get_declaration_period())
        return request

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["year"] = getattr(self.request, "year", None)
        return context
