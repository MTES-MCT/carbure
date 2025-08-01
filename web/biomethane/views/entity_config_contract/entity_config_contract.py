from drf_spectacular.utils import OpenApiParameter, extend_schema
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

    def list(self, request, *args, **kwargs):
        try:
            contract = BiomethaneEntityConfigContract.objects.get(entity=request.entity)
            data = self.get_serializer(contract).data
            return Response(data)

        except BiomethaneEntityConfigContract.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        try:
            contract = BiomethaneEntityConfigContract.objects.get(entity=request.entity)
            serializer = self.get_serializer(contract, data=request.data, partial=True)
            print("Partial update data:", request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneEntityConfigContract.DoesNotExist:
            return Response({"detail": "Contract not found for this entity."}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        serializer.save(entity=self.request.entity)
