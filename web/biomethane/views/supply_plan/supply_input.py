from django.db.models import Sum
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.filters import BiomethaneSupplyInputCreateFilter, BiomethaneSupplyInputFilter
from biomethane.models import BiomethaneSupplyInput
from biomethane.models.biomethane_contract import BiomethaneContract
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.supply_plan.supply_input import (
    BiomethaneSupplyInputCreateSerializer,
    BiomethaneSupplyInputExportSerializer,
    BiomethaneSupplyInputSerializer,
)
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
class BiomethaneSupplyInputViewSet(
    ListWithObjectPermissionsMixin,
    GenericViewSet,
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    ExcelExportActionMixin,
    FiltersActionFactory(),
):
    queryset = BiomethaneSupplyInput.objects.all()
    filterset_class = BiomethaneSupplyInputFilter
    search_fields = ["input_name"]
    pagination_class = BiomethaneSupplyInputPagination

    def get_permissions(self):
        return get_biomethane_permissions(["create", "update", "partial_update"], self.action)

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
        if self.action in ["list", "export_supply_plan_to_excel"]:
            return self.filterset_class
        return BiomethaneSupplyInputCreateFilter

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BiomethaneSupplyInputCreateSerializer
        elif self.action == "export_supply_plan_to_excel":
            return BiomethaneSupplyInputExportSerializer
        return BiomethaneSupplyInputSerializer
