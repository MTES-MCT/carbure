from django.db.models import Sum
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.filters import BiomethaneSupplyInputCreateFilter, BiomethaneSupplyInputFilter
from biomethane.models import BiomethaneSupplyInput
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.supply_plan.supply_input import (
    BiomethaneSupplyInputCreateSerializer,
    BiomethaneSupplyInputExportSerializer,
    BiomethaneSupplyInputSerializer,
)
from core.filters import FiltersActionMixin
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
    ]
)
class BiomethaneSupplyInputViewSet(
    GenericViewSet,
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    FiltersActionMixin,
    ExcelExportActionMixin,
):
    queryset = BiomethaneSupplyInput.objects.all()
    filterset_class = BiomethaneSupplyInputFilter
    search_fields = ["input_type", "input_category"]
    pagination_class = BiomethaneSupplyInputPagination

    def get_permissions(self):
        return get_biomethane_permissions(["create", "update", "partial_update"], self.action)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
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
