from django.db.models import Case, CharField, ExpressionWrapper, F, FloatField, OuterRef, Q, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce, Round
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.pagination import MetadataPageNumberPagination
from entity.permissions import HasDgddiWriteRights
from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.filters import OperationFilter
from tiruert.models import Operation, OperationDetail
from tiruert.permissions import HasTiruertRightsBalanceAndOperations, HasTiruertWriteRights, TiruertAdminRights
from tiruert.serializers import (
    OperationInputSerializer,
    OperationListSerializer,
    OperationSerializer,
    OperationUpdateSerializer,
)
from tiruert.services.declaration_period import DeclarationPeriodService
from tiruert.services.energy import (
    avoided_emissions_tco2_expression,
    energy_mj_expression,
)
from tiruert.services.teneur import GHG_REFERENCE_RED_II

from .mixins import ActionMixin


class OperationPagination(MetadataPageNumberPagination):
    aggregate_fields = {"total_volume": 0}

    def get_extra_metadata(self):
        queryset = getattr(self, "queryset", None)
        if callable(getattr(queryset, "aggregate", None)):
            return queryset.exclude_informative().aggregate(
                total_volume=Round(
                    Coalesce(
                        Sum(
                            ExpressionWrapper(
                                F("_volume"),
                                output_field=FloatField(),
                            )
                        ),
                        Value(0.0),
                    ),
                    precision=2,
                )
            )

        metadata = {"total_volume": 0}

        for operation in queryset or []:
            if operation.type in Operation.BALANCE_EXCLUDED_TYPES:
                continue
            metadata["total_volume"] += operation._volume
        metadata["total_volume"] = round(metadata["total_volume"], 2)
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
class OperationViewSet(ModelViewSet, ActionMixin):
    queryset = Operation.objects.all().order_by("pk")
    serializer_class = OperationListSerializer
    filterset_class = OperationFilter
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
            "download_import_template",
            "import_operations_from_excel",
            "declare_teneur",
        ]:
            return [HasTiruertWriteRights()]
        elif self.action == "correct":
            return [HasDgddiWriteRights()]
        return [(HasTiruertRightsBalanceAndOperations | HasDgddiWriteRights | TiruertAdminRights)()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["details"] = self.request.GET.get("details", "0") == "1"  # For debugging purposes
        if self.action in ["create", "update", "partial_update"]:
            context["declaration_year"] = DeclarationPeriodService.get_current_declaration_year()
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
        # Permissions to use selected_entity_id here are handled in the filter_entity() method of the OperationFilter
        entity_id = self.request.query_params.get("selected_entity_id") or self.request.entity.id
        details_requested = self.request.GET.get("details", "0") == "1"

        details_queryset = OperationDetail.objects.filter(operation_id=OuterRef("pk"))
        total_volume_subquery = details_queryset.values("operation_id").annotate(total=Sum("volume")).values("total")[:1]
        avoided_emissions_subquery = (
            details_queryset.values("operation_id")
            .annotate(
                total=Sum(
                    avoided_emissions_tco2_expression(
                        energy_mj_expression(
                            F("volume"),
                            F("operation__renewable_energy_share"),
                            F("lot__biofuel__pci_litre"),
                        ),
                        F("emission_rate_per_mj"),
                        GHG_REFERENCE_RED_II,
                    )
                )
            )
            .values("total")[:1]
        )

        total_volume_expr = Coalesce(
            Subquery(total_volume_subquery, output_field=FloatField()),
            Value(0.0),
        )
        sign_expr = Case(
            When(credited_entity_id=entity_id, then=Value(1.0)),
            When(debited_entity_id=entity_id, then=Value(-1.0)),
            default=Value(None),
            output_field=FloatField(),
        )

        annotations = {
            "_avoided_emissions": Coalesce(
                Subquery(avoided_emissions_subquery, output_field=FloatField()),
                Value(0.0),
            ),
            "_sector": Case(
                When(type=Operation.TENEUR, objective_sector__isnull=False, then=F("objective_sector")),
                When(biofuel__compatible_essence=True, then=Value("ESSENCE")),
                When(biofuel__compatible_diesel=True, then=Value("GAZOLE")),
                When(biofuel__code__in=SAF_BIOFUEL_TYPES, then=Value("CARBURÉACTEUR")),
                When(biofuel__compatible_gpl=True, then=Value("GPL")),
                When(biofuel__compatible_maritime=True, then=Value("MARITIME")),
                default=Value(None),
                output_field=CharField(),
            ),
            "_type": Case(
                When(Q(type="CESSION", credited_entity_id=entity_id), then=Value("ACQUISITION")),
                default=F("type"),
                output_field=CharField(),
            ),
            "_depot": Case(
                When(Q(type="CESSION", credited_entity_id=entity_id), then=F("to_depot__name")),
                When(Q(type="CESSION", debited_entity_id=entity_id), then=F("from_depot__name")),
                When(Q(type="INCORPORATION") | Q(type="MAC_BIO"), then=F("to_depot__name")),
                When(Q(type="EXPORTATION") | Q(type="EXPEDITION"), then=F("from_depot__name")),
                default=Value(None),
                output_field=CharField(),
            ),
            "_entity": Case(
                When(Q(type="CESSION", credited_entity_id=entity_id), then=F("debited_entity__name")),
                When(Q(type="CESSION", debited_entity_id=entity_id), then=F("credited_entity__name")),
                When(Q(type="TRANSFERT", credited_entity_id=entity_id), then=F("debited_entity__name")),
                When(Q(type="TRANSFERT", debited_entity_id=entity_id), then=F("credited_entity__name")),
                When(Q(type="EXPORTATION") | Q(type="EXPEDITION"), then=F("export_recipient")),
                default=Value(None),
                output_field=CharField(),
            ),
            "_volume": ExpressionWrapper(
                total_volume_expr * sign_expr,
                output_field=FloatField(),
            ),
            "_energy": energy_mj_expression(
                total_volume_expr,
                F("renewable_energy_share"),
                F("biofuel__pci_litre"),
                sign_expr,
            ),
            "_transaction": Case(
                When(credited_entity_id=entity_id, then=Value("CREDIT")),
                When(debited_entity_id=entity_id, then=Value("DEBIT")),
                default=Value(None),
                output_field=CharField(),
            ),
        }

        queryset = super().get_queryset().annotate(**annotations)

        if self.action == "list" and not details_requested:
            queryset = queryset.prefetch_related(None)
        elif self.action in ["retrieve", "correct", "export_operations_to_excel"] or details_requested:
            queryset = queryset.prefetch_related("details")

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
        if instance.type in Operation.API_DELETABLE_TYPES and instance.status in [
            Operation.PENDING,
            Operation.REJECTED,
            Operation.DRAFT,
        ]:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
