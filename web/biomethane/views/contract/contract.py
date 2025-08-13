from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from biomethane.models import BiomethaneContract
from biomethane.serializers.contract import (
    BiomethaneContractAddSerializer,
    BiomethaneContractPatchSerializer,
    BiomethaneContractSerializer,
)
from core.models import Entity
from core.permissions import HasUserRights

# from .mixins import ActionMixin


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
class BiomethaneContractViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
):
    queryset = BiomethaneContract.objects.all()
    serializer_class = BiomethaneContractSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneContractAddSerializer
        elif self.action in ["update"]:
            return BiomethaneContractPatchSerializer
        return BiomethaneContractSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneContractSerializer,
                description="Contract details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Contract not found for this entity."),
        },
        description="Retrieve the contract for the current entity. Returns a single contract object.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            contract = BiomethaneContract.objects.get(entity=request.entity)
            data = self.get_serializer(contract, many=False).data
            return Response(data)

        except BiomethaneContract.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneContractSerializer,
            ),
        },
        request=BiomethaneContractPatchSerializer,
    )
    def update(self, request, *args, **kwargs):
        try:
            contract = BiomethaneContract.objects.get(entity=request.entity)
            serializer = self.get_serializer(contract, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneContract.DoesNotExist:
            return Response({"detail": "Aucun contrat trouvé pour cette entité"}, status=status.HTTP_404_NOT_FOUND)
