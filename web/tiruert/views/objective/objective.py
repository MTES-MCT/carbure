from datetime import datetime

from django.utils.timezone import make_aware
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tiruert.filters import ObjectiveFilter, OperationFilter
from tiruert.models import MacFossilFuel, Objective, Operation
from tiruert.serializers import ObjectiveOutputSerializer
from tiruert.services.balance import BalanceService
from tiruert.services.objective import ObjectiveService
from tiruert.services.teneur import GHG_REFERENCE_RED_II


class ObjectiveViewSet(ModelViewSet):
    queryset = MacFossilFuel.objects.all()
    serializer_class = ObjectiveOutputSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = ObjectiveFilter
    filter_backends = [DjangoFilterBackend]
    http_method_names = ["get"]

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        # Get unit from request params or entity preference or default to liters
        entity = getattr(request, "entity", None)
        unit = request.GET.get("unit") or (entity.preferred_unit.lower() if entity else None) or "l"
        setattr(request, "unit", unit)
        return request

    def get_serializer_context(self):
        context = super().get_serializer_context()
        entity = self.request.entity
        context["entity_id"] = entity.id
        if getattr(self.request, "unit", None):
            context["unit"] = self.request.unit
        return context

    def list(self, request, *args, **kwargs):
        mac_qs = self.filter_queryset(self.get_queryset())
        year = request.GET.get("year") or datetime.now().year
        entity_id = request.entity.id
        date_from_str = request.query_params.get("date_from")
        date_from = make_aware(datetime.strptime(date_from_str, "%Y-%m-%d")) if date_from_str else None

        objectives_qs = ObjectiveService.objectives_settings(year)

        energy_basis = ObjectiveService.calculate_energy_basis(mac_qs, objectives_qs)

        operations = OperationFilter(request.GET, queryset=Operation.objects.all(), request=request).qs

        if date_from:
            operations_with_date_from = operations
            # Remove date_from filter from operations
            query_params = request.GET.copy()
            query_params.pop("date_from", None)
            filterset = OperationFilter(data=query_params, queryset=self.get_queryset(), request=request)
            operations = filterset.qs

        # First get the whole balance (from forever), so with no date_from filter
        balance_per_category = BalanceService.calculate_balance(operations, entity_id, "customs_category", "mj")
        balance_per_sector = BalanceService.calculate_balance(operations, entity_id, "sector", "mj")

        # Then update the balance with quantity and teneur details for requested dates (if any)
        operations = operations_with_date_from if date_from else operations

        balance_per_category = BalanceService.calculate_balance(
            operations, entity_id, "customs_category", "mj", balance_per_category, update_balance=True
        )
        balance_per_sector = BalanceService.calculate_balance(
            operations, entity_id, "sector", "mj", balance_per_sector, update_balance=True
        )

        objective_per_category = ObjectiveService.calculate_objective(
            balance_per_category,
            objectives_qs,
            energy_basis,
            Objective.BIOFUEL_CATEGORY,
        )

        objective_per_sector = ObjectiveService.calculate_objective(
            balance_per_sector,
            objectives_qs,
            energy_basis,
            Objective.SECTOR,
        )

        global_objective_target = ObjectiveService.calculate_global_objective(objectives_qs, energy_basis)

        global_objective = {
            "available_balance": sum([sector["available_balance"] for sector in objective_per_sector])
            * GHG_REFERENCE_RED_II
            / 1000000,
            "target": global_objective_target * GHG_REFERENCE_RED_II / 1000000,
            "pending_teneur": sum([sector["pending_teneur"] for sector in objective_per_sector])
            * GHG_REFERENCE_RED_II
            / 1000000,
            "declared_teneur": sum([sector["declared_teneur"] for sector in objective_per_sector])
            * GHG_REFERENCE_RED_II
            / 1000000,
            "unit": "tCO2",
        }

        result = {
            "main": global_objective,
            "sectors": objective_per_sector,
            "categories": objective_per_category,
        }

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
