from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from biomethane.decorators.check_declaration_period import CheckDeclarationPeriod
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading
from biomethane.serializers.digestate.spreading import (
    BiomethaneDigestateSpreadingAddSerializer,
)
from core.models import Entity, UserRights
from core.permissions import HasUserRights


@extend_schema_view(
    create=extend_schema(
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
    ),
    destroy=extend_schema(
        parameters=[
            OpenApiParameter(
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Authorised entity ID.",
                required=True,
            )
        ]
    ),
)
class BiomethaneDigestateSpreadingViewSet(GenericViewSet, CreateModelMixin, DestroyModelMixin):
    queryset = BiomethaneDigestateSpreading.objects.all()
    serializer_class = BiomethaneDigestateSpreadingAddSerializer
    permission_classes = [
        IsAuthenticated,
        HasUserRights(UserRights.RW, [Entity.BIOMETHANE_PRODUCER]),
        CheckDeclarationPeriod,
    ]
    http_method_names = ["post", "delete"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["year"] = self.request.query_params.get("year")
        return context

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Authorised entity ID.",
                required=True,
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
