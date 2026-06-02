from django.db.models import Sum
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters import BiomethaneSupplyInputFilter, BiomethaneSupplyInputYearFilter
from biomethane.models import BiomethaneContract, BiomethaneSupplyInput
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.supply_plan.supply_input import (
    BiomethaneSupplyInputCreateSerializer,
    BiomethaneSupplyInputExportSerializer,
    BiomethaneSupplyInputSerializer,
)
from biomethane.serializers.supply_plan.tariff_coefficient_proportions import TariffCoefficientProportionsSerializer
from biomethane.services.supply_plan.tariff_coefficient import compute_tariff_coefficient_proportions
from biomethane.views.mixins import ListWithObjectPermissionsMixin
from core.filters import FiltersActionFactory
from core.pagination import MetadataPageNumberPagination

from .mixins import ExcelExportActionMixin


class BiomethaneSupplyInputPagination(MetadataPageNumberPagination):
    aggregate_fields = {"annual_volumes_in_t": Sum("volume")}


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
        OpenApiParameter(
            name="producer_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Producer entity ID (optional, used by DREAL to filter specific producer).",
            required=False,
        ),
        OpenApiParameter(
            name="year",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Year of the supply plan.",
            required=True,
        ),
    ]
)
@extend_schema_view(
    retrieve=extend_schema(parameters=[OpenApiParameter(name="year", exclude=True)]),
    update=extend_schema(parameters=[OpenApiParameter(name="year", exclude=True)]),
    partial_update=extend_schema(parameters=[OpenApiParameter(name="year", exclude=True)]),
    destroy=extend_schema(parameters=[OpenApiParameter(name="year", exclude=True)]),
)
class BiomethaneSupplyInputViewSet(
    ListWithObjectPermissionsMixin,
    GenericViewSet,
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    ExcelExportActionMixin,
    FiltersActionFactory(),
):
    queryset = BiomethaneSupplyInput.objects.all()
    filterset_class = BiomethaneSupplyInputFilter
    search_fields = ["feedstock__name"]
    pagination_class = BiomethaneSupplyInputPagination

    def get_permissions(self):
        return get_biomethane_permissions(["create", "destroy", "update", "partial_update"], self.action)

    def get_permission_object(self, first_obj):
        """Check permissions on the supply plan of the supply inputs."""
        if first_obj:
            return first_obj.supply_plan

        # When queryset is empty, retrieve contract from request params to check permissions
        producer_id = self.request.query_params.get("producer_id")
        entity_id = self.request.query_params.get("entity_id")

        # DREAL case: producer_id provided
        if producer_id:
            return BiomethaneContract.objects.filter(producer_id=producer_id).first()

        # Producer case: use entity_id
        if entity_id:
            return BiomethaneContract.objects.filter(producer_id=entity_id).first()

        return None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["year"] = self.request.query_params.get("year")
        return context

    def get_filterset_class(self):
        if self.action not in ["destroy", "retrieve", "update", "partial_update"]:
            return BiomethaneSupplyInputYearFilter
        return BiomethaneSupplyInputFilter

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BiomethaneSupplyInputCreateSerializer
        elif self.action == "export_supply_plan_to_excel":
            return BiomethaneSupplyInputExportSerializer
        elif self.action == "tariff_coefficient_proportions":
            return TariffCoefficientProportionsSerializer
        return BiomethaneSupplyInputSerializer

    @extend_schema(
        responses={200: TariffCoefficientProportionsSerializer},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="tariff-coefficient-proportions",
    )
    def tariff_coefficient_proportions(self, request, *args, **kwargs):
        """Volume-weighted P1/P2/P3/P/Peff shares for the filtered supply plan inputs."""
        queryset = self.filter_queryset(self.get_queryset()).select_related(
            "feedstock",
            "supply_plan__producer__biomethane_contract",
        )
        data = compute_tariff_coefficient_proportions(queryset)
        serializer = TariffCoefficientProportionsSerializer(data)
        return Response(serializer.data)
