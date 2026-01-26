from django.db.models import Case, CharField, F, FloatField, Q, Value, When
from django.db.models.functions import Cast, Concat, ExtractMonth, ExtractYear
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Entity, UserRights
from core.pagination import MetadataPageNumberPagination
from core.permissions import HasUserRights
from tiruert.filters import ElecOperationFilter
from tiruert.models import ElecOperation
from tiruert.serializers import (
    ElecOperationInputSerializer,
    ElecOperationListSerializer,
    ElecOperationSerializer,
    ElecOperationUpdateSerializer,
)

from .mixins import ActionMixin


class ElecOperationPagination(MetadataPageNumberPagination):
    aggregate_fields = {"total_quantity": 0}

    def get_extra_metadata(self):
        metadata = {"total_quantity": 0}
        for operation in self.queryset:
            sign = 1 if operation.is_credit(self.request.entity.id) else -1
            value = operation.quantity * sign if operation.status != ElecOperation.REJECTED else 0
            metadata["total_quantity"] += value
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
    ]
)
class ElecOperationViewSet(ModelViewSet, ActionMixin):
    queryset = ElecOperation.objects.all().order_by("pk")
    serializer_class = ElecOperationListSerializer
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR]),
    )
    filterset_class = ElecOperationFilter
    filter_backends = [DjangoFilterBackend]
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = ElecOperationPagination

    def get_permissions(self):
        if self.action in ["reject", "accept", "create", "destroy"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW])]
        elif self.action in ["balance"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RO, UserRights.RW])]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        entity = self.request.entity
        context["entity_id"] = entity.id
        return context

    def get_queryset(self):
        entity_id = self.request.entity.id
        return (
            super()
            .get_queryset()
            .annotate(
                _operation=Case(
                    When(Q(type="CESSION", credited_entity_id=entity_id), then=Value("ACQUISITION")),
                    default=F("type"),
                    output_field=CharField(),
                ),
                _type=Case(
                    When(type__in=["ACQUISITION", "ACQUISITION_FROM_CPO"], then=Value("CREDIT")),
                    When(type__in=["CESSION", "TENEUR"], then=Value("DEBIT")),
                    default=Value(None),
                    output_field=CharField(),
                ),
                _entity=Case(
                    When(Q(type="CESSION", credited_entity_id=entity_id), then=F("debited_entity__name")),
                    When(Q(type="CESSION", debited_entity_id=entity_id), then=F("credited_entity__name")),
                    default=Value(None),
                    output_field=CharField(),
                ),
                _quantity=Case(
                    When(
                        credited_entity_id=entity_id,
                        then=F("quantity"),
                    ),
                    When(
                        debited_entity_id=entity_id,
                        then=F("quantity") * -1,
                    ),
                    default=Value(None),
                    output_field=FloatField(),
                ),
                _period=Concat(
                    ExtractYear("created_at", output_field=CharField()),
                    Case(
                        When(
                            created_at__month__lt=10,
                            then=Concat(Value("0"), Cast("created_at__month", output_field=CharField())),
                        ),
                        default=ExtractMonth("created_at", output_field=CharField()),
                        output_field=CharField(),
                    ),
                ),
            )
        )

    @extend_schema(
        operation_id="list_elec_operations",
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
            status.HTTP_200_OK: OpenApiResponse(response=ElecOperationListSerializer, description="A list of operations.")
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="get_elec_operation",
        description="Retrieve one specific operation.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ElecOperationSerializer, description="Details of specific operation."
            )
        },
    )
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ElecOperationSerializer
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        operation_id="create_elec_operation",
        description="Create a new operation.",
        request=ElecOperationInputSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=ElecOperationListSerializer, description="The newly created operation."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid input data."),
        },
        examples=[
            OpenApiExample(
                name="Create Operation Example",
                value={
                    "type": "TENEUR",
                    "credited_entity": "",
                    "debited_entity": 2,
                },
            )
        ],
    )
    def create(self, request):
        serializer = ElecOperationInputSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            operation = serializer.save()
            context = {"entity_id": self.request.entity.id}
            return Response(
                ElecOperationSerializer(operation, context=context).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="update_elec_operation",
        description="Update a part of operation.",
        request=ElecOperationUpdateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=ElecOperationSerializer, description="The updated operation."),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid input data."),
        },
        examples=[
            OpenApiExample(
                name="Update Operation Example",
                value={
                    "quantity": 10,
                },
            )
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ElecOperationUpdateSerializer(
            instance,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        if serializer.is_valid():
            operation = serializer.save()
            context = {"entity_id": self.request.entity.id}
            return Response(
                ElecOperationSerializer(operation, context=context).data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="delete_elec_operation",
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
        allowed_types = [ElecOperation.CESSION, ElecOperation.TENEUR]
        allowed_statuses = [ElecOperation.PENDING, ElecOperation.REJECTED]
        if instance.type in allowed_types and instance.status in allowed_statuses:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
