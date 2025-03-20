from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from tiruert.filters import MacFilter, ObjectiveFilter, OperationFilter
from tiruert.models import MacFossilFuel, Objective, Operation
from tiruert.serializers import ObjectiveOutputSerializer
from tiruert.services.objective import ObjectiveService


class ObjectiveViewSet(GenericViewSet):
    queryset = Objective.objects.all()
    filterset_class = ObjectiveFilter
    serializer_class = ObjectiveOutputSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    http_method_names = ["get"]
    pagination_class = None

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

    @extend_schema(
        operation_id="objectives",
        description="Get all objectives",
        parameters=[
            OpenApiParameter(
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Authorised entity ID.",
                required=True,
            ),
            OpenApiParameter(
                name="year",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Year of the objectives",
                required=True,
            ),
            OpenApiParameter(
                name="date_from",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Date from which to calculate balance for teneur",
                required=True,
            ),
            OpenApiParameter(
                name="date_to",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Date to which to calculate balance for teneur",
                required=True,
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ObjectiveOutputSerializer,
                description="All objectives.",
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        # Get queryset with filters for MacFossilFuel, Objective and Operation
        objectives = self.filter_queryset(self.get_queryset())
        macs = MacFilter(request.GET, queryset=MacFossilFuel.objects.all(), request=request).qs
        operations = OperationFilter(request.GET, queryset=Operation.objects.all(), request=request).qs

        entity_id = request.entity.id

        date_from = request.query_params.get("date_from")
        if not date_from:
            return Response({"date_from": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Calculate "assiette" used for objectives calculation
        energy_basis = ObjectiveService.calculate_energy_basis(macs, objectives)

        # 2. Calculate the balances per category and sector
        balance_per_category, balance_per_sector = ObjectiveService.get_balances_for_objectives_calculation(
            request, operations, entity_id
        )

        # 3. Calculate the objectives per category and sector
        objective_per_category = ObjectiveService.calculate_objective(
            balance_per_category,
            objectives,
            energy_basis,
            Objective.BIOFUEL_CATEGORY,
        )

        objective_per_sector = ObjectiveService.calculate_objective(
            balance_per_sector,
            objectives,
            energy_basis,
            Objective.SECTOR,
        )

        # 4. Calculate the global objective
        global_objective_target = ObjectiveService.calculate_global_objective(objectives, energy_basis)

        available_balance_sum = sum([sector["available_balance"] for sector in objective_per_sector])
        pending_teneur_sum = sum([sector["pending_teneur"] for sector in objective_per_sector])
        declared_teneur_sum = sum([sector["declared_teneur"] for sector in objective_per_sector])

        global_objective = {
            "available_balance": ObjectiveService.apply_ghg_conversion(available_balance_sum),
            "target": ObjectiveService.apply_ghg_conversion(global_objective_target),
            "pending_teneur": ObjectiveService.apply_ghg_conversion(pending_teneur_sum),
            "declared_teneur": ObjectiveService.apply_ghg_conversion(declared_teneur_sum),
            "unit": "tCO2",
        }

        result = {
            "main": global_objective,
            "sectors": objective_per_sector,
            "categories": objective_per_category,
        }

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
