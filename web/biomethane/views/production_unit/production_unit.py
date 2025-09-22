from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneProductionUnit
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.production_unit import (
    BiomethaneProductionUnitSerializer,
    BiomethaneProductionUnitUpsertSerializer,
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
class BiomethaneProductionUnitViewSet(GenericViewSet):
    queryset = BiomethaneProductionUnit.objects.all()
    serializer_class = BiomethaneProductionUnitSerializer
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert"], self.action)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "upsert":
            return BiomethaneProductionUnitUpsertSerializer
        return BiomethaneProductionUnitSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneProductionUnitSerializer,
                description="Production unit details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Production unit not found for this entity."),
        },
        description="Retrieve the production unit for the current entity. Returns a single production unit object.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            production_unit = BiomethaneProductionUnit.objects.get(producer=request.entity)
            data = self.get_serializer(production_unit, many=False).data
            return Response(data)

        except BiomethaneProductionUnit.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneProductionUnitSerializer,
                description="Production unit updated successfully",
            ),
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneProductionUnitSerializer,
                description="Production unit created successfully",
            ),
        },
        description="Create or update the production unit for the current entity (upsert operation).",
    )
    def upsert(self, request, *args, **kwargs):
        """Create or update production unit using upsert logic."""
        try:
            production_unit = BiomethaneProductionUnit.objects.get(producer=request.entity)
            serializer = self.get_serializer(production_unit, data=request.data, partial=True)
            status_code = status.HTTP_200_OK
        except BiomethaneProductionUnit.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            status_code = status.HTTP_201_CREATED

        if serializer.is_valid():
            production_unit = serializer.save()
            return Response(status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
