from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from biomethane.serializers.digestate.spreading import (
    BiomethaneDigestateSpreadingAddSerializer,
    BiomethaneDigestateSpreadingSerializer,
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
        OpenApiParameter(
            name="year",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Year.",
            required=True,
        ),
    ]
)
class BiomethaneDigestateSpreadingViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = BiomethaneDigestateSpreadingAddSerializer
    permission_classes = [IsAuthenticated, HasUserRights(UserRights.RW, [Entity.BIOMETHANE_PRODUCER])]
    http_method_names = ["post"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["year"] = self.request.query_params.get("year")
        return context
