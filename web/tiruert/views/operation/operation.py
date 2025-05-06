from django.db.models import Case, CharField, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Entity, UserRights
from core.pagination import MetadataPageNumberPagination
from core.permissions import HasUserRights
from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.filters import OperationFilter
from tiruert.models import Operation
from tiruert.serializers import (
    OperationInputSerializer,
    OperationListSerializer,
    OperationSerializer,
    OperationUpdateSerializer,
)

from .mixins import ActionMixin


class OperationPagination(MetadataPageNumberPagination):
    aggregate_fields = {"total_quantity": 0}

    def get_extra_metadata(self):
        metadata = {"total_quantity": 0}

        for operation in self.queryset:
            volume_sign = 1 if operation.is_credit(self.request.entity.id) else -1
            quantity = operation.volume_to_quantity(operation.volume * operation.renewable_energy_share, self.request.unit)
            metadata["total_quantity"] += quantity * volume_sign
        return metadata


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
        OpenApiParameter(
            name="unit",
            type=str,
            enum=[choice[0] for choice in Entity.UNIT_CHOICE],
            location=OpenApiParameter.QUERY,
            description="Specify the volume unit.",
        ),
    ]
)
class OperationViewSet(ModelViewSet, ActionMixin):
    queryset = Operation.objects.all()
    serializer_class = OperationListSerializer
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR]),
    )
    filterset_class = OperationFilter
    filter_backends = [DjangoFilterBackend]
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = OperationPagination

    def get_permissions(self):
        if self.action in ["reject", "accept", "simulate", "create", "partial_update", "destroy"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW])]
        elif self.action in ["balance"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RO, UserRights.RW])]
        return super().get_permissions()

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        # Get unit from request params or entity preference or default to liters
        entity = getattr(request, "entity", None)
        unit = (
            request.POST.get("unit", request.GET.get("unit")) or (entity.preferred_unit.lower() if entity else None) or "l"
        )
        setattr(request, "unit", unit.lower())
        return request

    def get_serializer_context(self):
        context = super().get_serializer_context()
        entity = self.request.entity
        context["entity_id"] = entity.id
        if getattr(self.request, "unit", None):
            context["unit"] = self.request.unit
        context["details"] = self.request.GET.get("details", "0") == "1"
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                _sector=Case(
                    When(biofuel__compatible_essence=True, then=Value("ESSENCE")),
                    When(biofuel__compatible_diesel=True, then=Value("GAZOLE")),
                    When(biofuel__code__in=SAF_BIOFUEL_TYPES, then=Value("CARBURÉACTEUR")),
                    default=Value(None),
                    output_field=CharField(),
                ),
                _type=Case(
                    When(Q(type="CESSION", credited_entity_id=self.request.entity.id), then=Value("ACQUISITION")),
                    default=F("type"),
                    output_field=CharField(),
                ),
                _depot=Coalesce(
                    "from_depot__name",
                    "to_depot__name",
                ),
                _entity=Case(
                    When(Q(type="CESSION", credited_entity_id=self.request.entity.id), then=F("debited_entity__name")),
                    When(Q(type="CESSION", debited_entity_id=self.request.entity.id), then=F("credited_entity__name")),
                    default=F("credited_entity__name"),
                    output_field=CharField(),
                ),
                _volume=Sum("details__volume"),
            )
        )

    @extend_schema(
        operation_id="list_operations",
        description="Retrieve a list of operations with optional filtering and pagination.",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="details",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Include detailed information if set to `1`.",
                default="0",
            )
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=OperationListSerializer, description="A list of operations.")
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="get_operation",
        description="Retrieve one specific operation.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=OperationSerializer, description="Details of specific operation.")
        },
    )
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = OperationSerializer
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        operation_id="create_operation",
        description="Create a new operation.",
        request=OperationInputSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=OperationListSerializer, description="The newly created operation."
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
                    "lots": [
                        {"id": 10, "volume": 39462, "emission_rate_per_mj": 5.25},
                        {"id": 11, "volume": 723.2, "emission_rate_per_mj": 30.2},
                    ],
                },
            )
        ],
    )
    def create(self, request):
        entity_id = self.request.GET.get("entity_id")
        serializer = OperationInputSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            operation = serializer.save()
            return Response(
                OperationSerializer(operation, context={"details": 1, "entity_id": entity_id}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="update_operation",
        description="Update a part of operation.",
        request=OperationUpdateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=OperationSerializer, description="The updated operation."),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid input data."),
        },
        examples=[
            OpenApiExample(
                name="Update Operation Example",
                value={
                    "to_depot": 10,
                },
            )
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        entity_id = self.request.GET.get("entity_id")
        serializer = OperationUpdateSerializer(
            instance,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        if serializer.is_valid():
            operation = serializer.save()
            return Response(
                OperationSerializer(operation, context={"details": 1, "entity_id": entity_id}).data,
                status=status.HTTP_200_OK,
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
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.type in [Operation.CESSION, Operation.TENEUR] and instance.status in [
            Operation.PENDING,
            Operation.REJECTED,
        ]:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
