from django.db.models import Case, CharField, F, FloatField, Q, Sum, Value, When
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Entity
from core.pagination import MetadataPageNumberPagination
from entity.permissions import HasDgddiWriteRights, HasOperatorRights, HasOperatorWriteRights
from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.filters import OperationFilter
from tiruert.models import Operation
from tiruert.serializers import (
    OperationInputSerializer,
    OperationListSerializer,
    OperationSerializer,
    OperationUpdateSerializer,
)
from tiruert.views.mixins import UnitMixin

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
class OperationViewSet(UnitMixin, ModelViewSet, ActionMixin):
    queryset = Operation.objects.all()
    serializer_class = OperationListSerializer
    filterset_class = OperationFilter
    filter_backends = [DjangoFilterBackend]
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = OperationPagination

    def get_permissions(self):
        if self.action in [
            "reject",
            "accept",
            "simulate",
            "simulate_min_max",
            "create",
            "update",
            "partial_update",
            "destroy",
            "export_operations_to_excel",
            "declare_teneur",
        ]:
            return [HasOperatorWriteRights()]
        elif self.action == "correct":
            return [HasDgddiWriteRights()]
        return [(HasOperatorRights | HasDgddiWriteRights)()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["details"] = self.request.GET.get("details", "0") == "1"  # For debugging purposes
        return context

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OperationSerializer
        elif self.action == "create":
            return OperationInputSerializer
        elif self.action == "partial_update":
            return OperationUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        multiplicators = {
            "mj": "biofuel__pci_litre",
            "kg": "biofuel__masse_volumique",
        }
        multiplicator = multiplicators.get(self.request.unit, None)
        entity_id = self.request.entity.id

        queryset = (
            super()
            .get_queryset()
            .annotate(
                total_volume=Sum("details__volume"),
                _sector=Case(
                    When(biofuel__compatible_essence=True, then=Value("ESSENCE")),
                    When(biofuel__compatible_diesel=True, then=Value("GAZOLE")),
                    When(biofuel__code__in=SAF_BIOFUEL_TYPES, then=Value("CARBURÉACTEUR")),
                    default=Value(None),
                    output_field=CharField(),
                ),
                _type=Case(
                    When(Q(type="CESSION", credited_entity_id=entity_id), then=Value("ACQUISITION")),
                    default=F("type"),
                    output_field=CharField(),
                ),
                _depot=Case(
                    When(Q(type="CESSION", credited_entity_id=entity_id), then=F("to_depot__name")),
                    When(Q(type="CESSION", debited_entity_id=entity_id), then=F("from_depot__name")),
                    When(Q(type="INCORPORATION") | Q(type="MAC_BIO"), then=F("to_depot__name")),
                    When(Q(type="EXPORTATION") | Q(type="EXPEDITION"), then=F("from_depot__name")),
                    default=Value(None),
                    output_field=CharField(),
                ),
                _entity=Case(
                    When(Q(type="CESSION", credited_entity_id=entity_id), then=F("debited_entity__name")),
                    When(Q(type="CESSION", debited_entity_id=entity_id), then=F("credited_entity__name")),
                    When(Q(type="TRANSFERT", credited_entity_id=entity_id), then=F("debited_entity__name")),
                    When(Q(type="TRANSFERT", debited_entity_id=entity_id), then=F("credited_entity__name")),
                    When(Q(type="EXPORTATION") | Q(type="EXPEDITION"), then=F("export_recipient")),
                    default=Value(None),
                    output_field=CharField(),
                ),
                _quantity=Case(
                    When(
                        credited_entity_id=entity_id,
                        then=F("total_volume") * (F(multiplicator) if multiplicator else 1),
                    ),
                    When(
                        debited_entity_id=entity_id,
                        then=F("total_volume") * -1 * (F(multiplicator) if multiplicator else 1),
                    ),
                    default=Value(None),
                    output_field=FloatField(),
                ),
                _volume=Case(
                    When(
                        credited_entity_id=entity_id,
                        then=F("total_volume"),
                    ),
                    When(
                        debited_entity_id=entity_id,
                        then=F("total_volume") * -1,
                    ),
                    default=Value(None),
                    output_field=FloatField(),
                ),
                _transaction=Case(
                    When(credited_entity_id=entity_id, then=Value("CREDIT")),
                    When(debited_entity_id=entity_id, then=Value("DEBIT")),
                    default=Value(None),
                    output_field=CharField(),
                ),
            )
        )

        # exclude operations that are drafts and credits
        queryset = queryset.exclude(Q(_transaction="CREDIT", status=Operation.DRAFT))

        return queryset

    def create(self, request):
        entity_id = request.entity.id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            operation = serializer.save()
            return Response(
                OperationSerializer(operation, context={"details": 1, "entity_id": entity_id}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        entity_id = self.request.GET.get("entity_id")
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            operation = serializer.save()
            return Response(
                OperationSerializer(operation, context={"details": 1, "entity_id": entity_id}).data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.type in [
            Operation.CESSION,
            Operation.TENEUR,
            Operation.TRANSFERT,
            Operation.EXPORTATION,
            Operation.EXPEDITION,
        ] and instance.status in [
            Operation.PENDING,
            Operation.REJECTED,
            Operation.DRAFT,
        ]:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
