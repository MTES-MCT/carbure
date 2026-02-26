from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import HasAdminRights, HasUserRights
from tiruert.filters import MacFilter, ObjectiveFilter, OperationFilterForBalance
from tiruert.filters.elec_operation import ElecOperationFilterForBalance
from tiruert.models import MacFossilFuel, Objective, Operation
from tiruert.models.elec_operation import ElecOperation
from tiruert.serializers import ObjectiveAdminInputSerializer, ObjectiveInputSerializer, ObjectiveOutputSerializer
from tiruert.services.objective import ObjectiveService
from tiruert.views.mixins import UnitMixin


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
            name="year",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Year of the objectives",
            required=True,
        ),
        OpenApiParameter(
            name="date_from",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Date from which to calculate balance for teneur",
            required=True,
        ),
        OpenApiParameter(
            name="date_to",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Date to which to calculate balance for teneur",
            required=True,
        ),
    ]
)
class ObjectiveViewSet(UnitMixin, GenericViewSet):
    queryset = Objective.objects.all()
    filterset_class = ObjectiveFilter
    serializer_class = ObjectiveOutputSerializer
    http_method_names = ["get"]
    pagination_class = None

    def initial(self, request, *args, **kwargs):
        """Reset execution cache for each request to avoid concurrency issues."""
        super().initial(request, *args, **kwargs)
        self._execution_cache = {}

    def get_permissions(self):
        if self.action in ["get_objectives_admin_view", "get_agregated_objectives_admin_view"]:
            return [HasAdminRights(allow_external=[ExternalAdminRights.TIRIB_STATS])]
        else:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW, UserRights.RO], [Entity.OPERATOR])]

    def get_objectives(self, request):
        """Get all objectives"""

        data = ObjectiveInputSerializer(data=request.GET)
        if not data.is_valid():
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

        result = self._get_objectives(request, request.entity.id)
        if result is None:
            return Response({}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="selected_entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Entity's objectives.",
                required=True,
            ),
        ]
    )
    def get_objectives_admin_view(self, request):
        """Get objectives for a specific entity - admin view"""

        data = ObjectiveAdminInputSerializer(data=request.GET)
        if not data.is_valid():
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

        selected_entity = data.validated_data.get("selected_entity_id")

        result = self._get_objectives(request, selected_entity.id)
        if result is None:
            return Response({}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_agregated_objectives_admin_view(self, request):
        """Get agregated objectives for all entities - admin view"""

        # Retrieve all entities that are liable for Tiruert
        tiruert_liable_entities = Entity.objects.filter(is_tiruert_liable=True)
        if not tiruert_liable_entities.exists():
            return Response({"error": "No Tiruert liable entities found."}, status=status.HTTP_404_NOT_FOUND)

        # Collect objectives for each entity
        objectives_list = []
        for entity in tiruert_liable_entities:
            try:
                entity_objectives = self._get_objectives(request, entity.id)
                if entity_objectives:
                    objectives_list.append(entity_objectives)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not objectives_list:
            return Response({}, status=status.HTTP_200_OK)

        # Aggregate all objectives
        result = ObjectiveService.aggregate_objectives(objectives_list)

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_objectives(self, request, target_entity_id):
        """Internal method to get objectives for a specific entity."""

        date_from = request.query_params.get("date_from")
        query_params = request.GET.copy()
        query_params["entity_id"] = target_entity_id

        # Get queryset with filters for MacFossilFuel, Objective and Operation
        # Objectives
        if self._execution_cache.get("objectives") is not None:
            objectives = self._execution_cache["objectives"]
        else:
            objectives = self.filter_queryset(self.get_queryset())
            if not objectives.exists():
                raise Http404("No objectives found.")
            else:
                self._execution_cache["objectives"] = objectives

        # MacFossilFuel
        macs = MacFilter(query_params, queryset=MacFossilFuel.objects.all(), request=request).qs
        if not macs.exists():
            return

        # Operations
        operations_qs = Operation.objects.all()
        operations = OperationFilterForBalance(query_params, queryset=operations_qs, request=request).qs
        if not operations.exists():
            return

        # 1. Calculate "assiette" used for objectives calculation (global, for categories and main objective)
        energy_basis = ObjectiveService.calculate_energy_basis(macs, year=query_params.get("year"))

        # 2. Calculate the balances per category and sector
        balance_per_category, balance_per_sector = ObjectiveService.get_balances_for_objectives_calculation(
            operations, target_entity_id, date_from
        )

        # 3. Calculate the objectives per category (using global energy_basis)
        objective_per_category = ObjectiveService.calculate_objectives_and_penalties(
            balance_per_category,
            objectives,
            Objective.BIOFUEL_CATEGORY,
            energy_basis=energy_basis,
        )

        # 4. Calculate the objectives per sector (using sector-specific energy_basis)
        objective_per_sector = ObjectiveService.calculate_objectives_and_penalties(
            balance_per_sector,
            objectives,
            Objective.SECTOR,
            mac_queryset=macs,
            year=query_params.get("year"),
        )

        # 5. Calculate elec category
        elec_ops = ElecOperationFilterForBalance(query_params, queryset=ElecOperation.objects.all(), request=request).qs
        elec_category = ObjectiveService.get_elec_category(elec_ops, target_entity_id, date_from)

        # 6. Calculate the global objective (aggregated from sectors + elec)
        global_objective = ObjectiveService.calculate_global_objective(
            objective_per_sector, elec_category, objectives, energy_basis
        )

        # 6. Return the results
        return {
            "main": global_objective,
            "sectors": objective_per_sector,
            "categories": [*objective_per_category, elec_category],
        }
