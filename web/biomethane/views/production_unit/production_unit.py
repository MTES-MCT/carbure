from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from biomethane.models import BiomethaneProductionUnit
from biomethane.serializers.production_unit import (
    BiomethaneProductionUnitAddSerializer,
    BiomethaneProductionUnitPatchSerializer,
    BiomethaneProductionUnitSerializer,
)
from core.models import Entity
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
class BiomethaneProductionUnitViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
):
    queryset = BiomethaneProductionUnit.objects.all()
    serializer_class = BiomethaneProductionUnitSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneProductionUnitAddSerializer
        elif self.action in ["update"]:
            return BiomethaneProductionUnitPatchSerializer
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

    def update(self, request, *args, **kwargs):
        try:
            production_unit = BiomethaneProductionUnit.objects.get(producer=request.entity)
            serializer = self.get_serializer(production_unit, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneProductionUnit.DoesNotExist:
            return Response(
                {"detail": "Aucune unité de production trouvée pour cette entité"}, status=status.HTTP_404_NOT_FOUND
            )
