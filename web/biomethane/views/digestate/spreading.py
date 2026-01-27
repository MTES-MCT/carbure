from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.digestate.spreading import (
    BiomethaneDigestateSpreadingAddSerializer,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
        OpenApiParameter(
            name="producer_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Producer entity ID (optional, used by DREAL to filter specific producer).",
            required=False,
        ),
    ]
)
class BiomethaneDigestateSpreadingViewSet(GenericViewSet, CreateModelMixin, DestroyModelMixin):
    queryset = BiomethaneDigestateSpreading.objects.all()
    serializer_class = BiomethaneDigestateSpreadingAddSerializer

    def get_permissions(self):
        return get_biomethane_permissions(["create", "destroy"], self.action)
