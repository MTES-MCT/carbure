from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from biomethane.models import BiomethaneEntityConfigContract
from biomethane.serializers.entity_config_contract import (
    BiomethaneEntityConfigContractAddSerializer,
    BiomethaneEntityConfigContractPatchSerializer,
    BiomethaneEntityConfigContractSerializer,
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
class BiomethaneEntityConfigContractViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    queryset = BiomethaneEntityConfigContract.objects.all()
    serializer_class = BiomethaneEntityConfigContractSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneEntityConfigContractAddSerializer
        elif self.action in ["update", "partial_update"]:
            return BiomethaneEntityConfigContractPatchSerializer
        return BiomethaneEntityConfigContractSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneEntityConfigContractSerializer,
                description="Contract details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Contract not found for this entity."),
        },
        description="Retrieve the contract for the current entity. Returns a single contract object.",
    )
    def contract_get(self, request, *args, **kwargs):
        try:
            contract = BiomethaneEntityConfigContract.objects.get(entity=request.entity)
            data = self.get_serializer(contract, many=False).data
            return Response(data)

        except BiomethaneEntityConfigContract.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def contract_patch(self, request, *args, **kwargs):
        try:
            contract = BiomethaneEntityConfigContract.objects.get(entity=request.entity)
            serializer = self.get_serializer(contract, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneEntityConfigContract.DoesNotExist:
            return Response({"detail": "Contract not found for this entity."}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        serializer.save(entity=self.request.entity)
