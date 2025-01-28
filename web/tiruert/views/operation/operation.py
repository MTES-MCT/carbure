from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Entity, UserRights
from tiruert.filters import OperationFilter
from tiruert.models import Operation
from tiruert.permissions import HasUserRights
from tiruert.serializers import OperationInputSerializer, OperationOutputSerializer

from .mixins import ActionMixin


class OperationViewSet(ModelViewSet, ActionMixin):
    queryset = Operation.objects.all()
    serializer_class = OperationOutputSerializer
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR]),
    )
    filterset_class = OperationFilter
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ["reject", "accept", "balance"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW])]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        entity_id = self.request.GET.get("entity_id")
        details = self.request.GET.get("details", "0") == "1"
        unit = self.request.GET.get("unit", "l")
        kwargs["context"] = self.get_serializer_context()
        kwargs["context"]["entity_id"] = entity_id
        kwargs["context"]["details"] = details
        kwargs["context"]["unit"] = unit
        return super().get_serializer(*args, **kwargs)

    @extend_schema(
        operation_id="list_operations",
        description="Retrieve a list of operations with optional filtering and pagination.",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Authorised entity ID.",
                required=True,
            ),
            OpenApiParameter(
                name="details",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Include detailed information if set to `1`.",
                default="0",
            ),
            OpenApiParameter(
                name="unit",
                type=str,
                enum=["l", "mj"],
                location=OpenApiParameter.QUERY,
                description="Specify the volume unit (default is `l`).",
                default="l",
            ),
            OpenApiParameter(
                name="sector",
                type=str,
                many=True,
                enum=["ESSENCE", "DIESEL", "SAF"],
                location=OpenApiParameter.QUERY,
                description="",
            ),
            OpenApiParameter(
                name="depot",
                type=str,
                many=True,
                location=OpenApiParameter.QUERY,
                description="",
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=OperationOutputSerializer, description="A list of operations.")
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="create_operation",
        description="Create a new operation.",
        request=OperationInputSerializer,
        parameters=[
            OpenApiParameter(
                name="entity_id", type=str, location=OpenApiParameter.QUERY, description="Authorised entity ID."
            )
        ],
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=OperationOutputSerializer, description="The newly created operation."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid input data."),
        },
        examples=[
            OpenApiExample(
                name="Create Operation Example",
                value={
                    "type": "TENEUR",
                    "customs_category": "CONV",
                    "biofuel": 33,
                    "credited_entity": "",
                    "debited_entity": 2,
                    "depot": "",
                    "validity_date": "2025-01-03",
                    "lots": [
                        {"id": 10, "volume": 39462, "emission_rate_per_mj": 5.25},
                        {"id": 11, "volume": 723.2, "emission_rate_per_mj": 30.2},
                    ],
                },
            )
        ],
    )
    def create(self, request):
        serializer = OperationInputSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            operation = serializer.save()
            return Response(
                OperationOutputSerializer(operation, context={"details": 1}).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="delete_operation",
        description="Delete an operation. Only allowed for certain types and statuses.",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Operation deleted successfully."),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Forbidden. The operation type or status does not allow deletion."
            ),
        },
        parameters=[
            OpenApiParameter(
                name="entity_id", type=str, location=OpenApiParameter.QUERY, description="Authorised entity ID."
            ),
        ],
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.type == Operation.CESSION and instance.status in [Operation.PENDING, Operation.REJECTED]:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
