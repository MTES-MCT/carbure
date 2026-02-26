from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, extend_schema
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
from tiruert.services.declaration_period import DeclarationPeriodService
from tiruert.services.objective import ObjectiveService
from tiruert.services.objective_snapshot import ObjectiveSnapshotService
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

        data = ObjectiveInputSerializer(data=request.GET)
        if not data.is_valid():
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

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
            except Http404:
                # Case where no objectives are found for the entity, we simply skip it
                continue

        if not objectives_list:
            return Response({}, status=status.HTTP_200_OK)

        # Aggregate all objectives
        result = ObjectiveService.aggregate_objectives(objectives_list)

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_objectives(self, request, target_entity_id):
        """Internal method to get objectives for a specific entity."""

        query_params = request.GET.copy()
        query_params["entity_id"] = target_entity_id
        requested_year = int(query_params.get("year"))

        # Use snapshot for past declaration years if available
        if "current_year" not in self._execution_cache:
            self._execution_cache["current_year"] = DeclarationPeriodService.get_current_declaration_year()
        current_year = self._execution_cache["current_year"]

        if current_year and requested_year < current_year:
            snapshot_data = ObjectiveSnapshotService.get_snapshot(target_entity_id, requested_year)
            if snapshot_data is not None:
                return snapshot_data

        # Derive date_from from the declaration period for the requested year
        if "period" not in self._execution_cache:
            self._execution_cache["period"] = DeclarationPeriodService.get_period_by_year(requested_year)
        period = self._execution_cache["period"]
        if period is None:
            return None
        date_from = period.start_date

        # Objectives (shared across all entities for the same request)
        if "objectives" in self._execution_cache:
            objectives = self._execution_cache["objectives"]
        else:
            objectives = self.filter_queryset(self.get_queryset())
            if not objectives.exists():
                raise Http404("No objectives found.")
            self._execution_cache["objectives"] = objectives

        # MacFossilFuel
        macs = MacFilter(query_params, queryset=MacFossilFuel.objects.all(), request=request).qs
        if not macs.exists():
            return

        # Operations
        operations = OperationFilterForBalance(query_params, queryset=Operation.objects.all(), request=request).qs
        if not operations.exists():
            return

        elec_ops = ElecOperationFilterForBalance(query_params, queryset=ElecOperation.objects.all(), request=request).qs

        return ObjectiveService.build_objectives_result(
            objectives, macs, operations, elec_ops, target_entity_id, date_from, year=query_params.get("year")
        )
