from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

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
class BiomethaneContractViewSet(GenericViewSet):
    queryset = BiomethaneContract.objects.all()
    serializer_class = BiomethaneContractSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "upsert":
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
    def upsert(self, request, *args, **kwargs):
        """Create or update contract using upsert logic."""
        serializer_context = self.get_serializer_context()
        try:
            # Try to get existing contract
            contract = BiomethaneContract.objects.get(entity=request.entity)
            # Update existing contract
            serializer = BiomethaneContractPatchSerializer(
                contract, data=request.data, partial=True, context=serializer_context
            )
            if serializer.is_valid():
                serializer.save()
                response_data = BiomethaneContractSerializer(contract, context=serializer_context).data
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneContract.DoesNotExist:
            # Create new contract
            serializer = BiomethaneContractAddSerializer(data=request.data, context=serializer_context)
            if serializer.is_valid():
                contract = serializer.save()
                response_data = BiomethaneContractSerializer(contract, context=serializer_context).data
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
