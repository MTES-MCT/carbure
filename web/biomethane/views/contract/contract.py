from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters import BiomethaneContractFilter
from biomethane.models import BiomethaneContract
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.contract import (
    BiomethaneContractInputSerializer,
    BiomethaneContractSerializer,
)
from biomethane.views.mixins import WatchedFieldsActionMixin

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
class BiomethaneContractViewSet(GenericViewSet, WatchedFieldsActionMixin):
    queryset = BiomethaneContract.objects.all()
    filterset_class = BiomethaneContractFilter
    serializer_class = BiomethaneContractSerializer
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert"], self.action)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "upsert":
            return BiomethaneContractInputSerializer
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
            contract = self.filter_queryset(self.get_queryset()).get()
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
        request=BiomethaneContractInputSerializer,
    )
    def upsert(self, request, *args, **kwargs):
        """Create or update contract using upsert logic."""
        try:
            contract = self.filter_queryset(self.get_queryset()).get()
            serializer = self.get_serializer(contract, data=request.data, partial=True)
            status_code = status.HTTP_200_OK
        except BiomethaneContract.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            status_code = status.HTTP_201_CREATED

        if serializer.is_valid():
            serializer.save()
            return Response(status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
