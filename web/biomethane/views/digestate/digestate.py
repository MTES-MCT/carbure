from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.digestate import BiomethaneDigestateFilter
from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.serializers.digestate import (
    BiomethaneDigestateAddSerializer,
    BiomethaneDigestatePatchSerializer,
    BiomethaneDigestateSerializer,
)
from biomethane.utils import get_declaration_period
from biomethane.views.digestate.mixins import ValidateActionMixin, YearsActionMixin
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
class BiomethaneDigestateViewSet(GenericViewSet, YearsActionMixin, ValidateActionMixin):
    queryset = BiomethaneDigestate.objects.all()
    serializer_class = BiomethaneDigestateSerializer
    permission_classes = [HasUserRights(entity_type=[Entity.BIOMETHANE_PRODUCER])]
    filterset_class = BiomethaneDigestateFilter
    pagination_class = None

    def get_permissions(self):
        if self.action in [
            "upsert",
            "validate_digestate",
        ]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return super().get_permissions()

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        setattr(request, "year", get_declaration_period())
        return request

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["year"] = getattr(self.request, "year", None)
        return context

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Digestate not found for this entity."),
        },
        description="Retrieve the digestate for the current entity and the current year. Returns a single digestate object.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            digestate = BiomethaneDigestate.objects.get(producer=request.entity, year=request.year)
            data = self.get_serializer(digestate, many=False).data
            return Response(data)

        except BiomethaneDigestate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate updated successfully",
            ),
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate created successfully",
            ),
        },
        request=BiomethaneDigestateAddSerializer,
        description="Create or update the digestate for the current entity (upsert operation).",
    )
    def upsert(self, request, *args, **kwargs):
        serializer_context = self.get_serializer_context()

        try:
            digestate = BiomethaneDigestate.objects.get(producer=request.entity, year=request.year)
            serializer = BiomethaneDigestatePatchSerializer(
                digestate, data=request.data, partial=True, context=serializer_context
            )
            status_code = status.HTTP_200_OK
        except BiomethaneDigestate.DoesNotExist:
            serializer = BiomethaneDigestateAddSerializer(data=request.data, context=serializer_context)
            status_code = status.HTTP_201_CREATED

        if serializer.is_valid():
            digestate = serializer.save()
            return Response(status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
