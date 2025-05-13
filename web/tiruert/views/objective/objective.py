from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Entity, UserRights
from core.permissions import HasAdminRights, HasUserRights
from tiruert.filters import MacFilter, ObjectiveFilter, OperationFilterForBalance
from tiruert.models import MacFossilFuel, Objective, Operation
from tiruert.serializers import ObjectiveAdminInputSerializer, ObjectiveInputSerializer, ObjectiveOutputSerializer
from tiruert.services.objective import ObjectiveService


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
class ObjectiveViewSet(GenericViewSet):
    queryset = Objective.objects.all()
    filterset_class = ObjectiveFilter
    serializer_class = ObjectiveOutputSerializer
    filter_backends = [DjangoFilterBackend]
    http_method_names = ["get"]
    pagination_class = None
    _execution_cache = {}

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        # Get unit from request params or entity preference or default to liters
        entity = getattr(request, "entity", None)
        unit = (
            request.POST.get("unit", request.GET.get("unit")) or (entity.preferred_unit.lower() if entity else None) or "l"
        )
        setattr(request, "unit", unit.lower())

        return request

    def get_serializer_context(self):
        context = super().get_serializer_context()
        entity = self.request.entity
        context["entity_id"] = entity.id
        if getattr(self.request, "unit", None):
            context["unit"] = self.request.unit
        return context

    def get_permissions(self):
        if self.action in ["get_objectives_admin_view", "get_agregated_objectives_admin_view"]:
            self.permission_classes = [IsAuthenticated, HasAdminRights]
        else:
            self.permission_classes = [
                IsAuthenticated,
                HasUserRights([UserRights.ADMIN, UserRights.RW, UserRights.RO], [Entity.OPERATOR]),
            ]

        return super().get_permissions()

    @extend_schema(
        operation_id="objectives",
        description="Get all objectives",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ObjectiveOutputSerializer,
                description="All objectives.",
            ),
        },
    )
    def get_objectives(self, request):
        data = ObjectiveInputSerializer(data=request.GET)
        if not data.is_valid():
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

        result = self._get_objectives(request)
        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="objectives",
        description="Get objectives for a specific entity - admin view",
        parameters=[
            OpenApiParameter(
                name="selected_entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Entity's objectives.",
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
    def get_objectives_admin_view(self, request):
        data = ObjectiveAdminInputSerializer(data=request.GET)
        if not data.is_valid():
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

        selected_entity = data.validated_data.get("selected_entity_id")

        setattr(request, "entity", selected_entity)
        query_params = request.GET.copy()
        query_params["entity_id"] = selected_entity.id

        result = self._get_objectives(request, query_params)
        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="objectives",
        description="Get agregated objectives for all entities - admin view",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ObjectiveOutputSerializer,
                description="All agregated objectives for all liable enttities.",
            ),
        },
    )
    def get_agregated_objectives_admin_view(self, request):
        # Retrieve all entities that are liable for Tiruert
        tiruert_liable_entities = Entity.objects.filter(is_tiruert_liable=True)
        if not tiruert_liable_entities.exists():
            return Response({"error": "No Tiruert liable entities found."}, status=status.HTTP_404_NOT_FOUND)

        # Initialize aggregated results
        aggregated_main = {
            "available_balance": 0,
            "target": 0,
            "pending_teneur": 0,
            "declared_teneur": 0,
            "unit": "tCO2",
            "target_percent": None,
            "penalty": 0,
        }

        aggregated_sectors = {}
        aggregated_categories = {}

        original_entity = request.entity
        # Process each entity
        for entity in tiruert_liable_entities:
            # Temporarily set the request entity to the current entity
            setattr(request, "entity", entity)
            query_params = request.GET.copy()
            query_params["entity_id"] = entity.id
            try:
                # Get objectives for the current entity
                entity_objectives = self._get_objectives(request, query_params)
                if not entity_objectives:
                    continue

                # Aggregate main objectives
                for key in ["available_balance", "target", "pending_teneur", "declared_teneur", "penalty"]:
                    if key in entity_objectives["main"]:
                        aggregated_main[key] += entity_objectives["main"][key]

                # Preserve target_percent (should be the same for all entities)
                if aggregated_main["target_percent"] is None and "target_percent" in entity_objectives["main"]:
                    aggregated_main["target_percent"] = entity_objectives["main"]["target_percent"]

                # Aggregate sectors
                for sector in entity_objectives["sectors"]:
                    code = sector["code"]
                    if code not in aggregated_sectors:
                        aggregated_sectors[code] = sector.copy()
                    else:
                        for key, value in sector.items():
                            if key in ["pending_teneur", "declared_teneur", "available_balance"]:
                                aggregated_sectors[code][key] += value
                            elif key == "objective":
                                for objective_key, objective_value in value.items():
                                    if objective_key in ["target_mj", "penalty"]:
                                        aggregated_sectors[code]["objective"][objective_key] += objective_value

                # Aggregate categories
                for category in entity_objectives["categories"]:
                    code = category["code"]
                    if code not in aggregated_categories:
                        aggregated_categories[code] = category.copy()
                    else:
                        for key, value in category.items():
                            if key in ["pending_teneur", "declared_teneur", "available_balance"]:
                                aggregated_categories[code][key] += value
                            elif key == "objective":
                                for objective_key, objective_value in value.items():
                                    if objective_key in ["target_mj", "penalty"]:
                                        aggregated_categories[code]["objective"][objective_key] += objective_value

            except Exception as e:
                if isinstance(e, ValueError):
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                if isinstance(e, Http404):
                    return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(
                        {"error": f"An unexpected error occurred. : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        # Restore the original entity
        setattr(request, "entity", original_entity)

        # Convert aggregated dictionaries to lists
        aggregated_sectors_list = list(aggregated_sectors.values())
        aggregated_categories_list = list(aggregated_categories.values())

        # Final result
        result = {
            "main": aggregated_main,
            "sectors": aggregated_sectors_list,
            "categories": aggregated_categories_list,
        }

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_objectives(self, request, query_params=None):
        entity_id = request.entity.id
        date_from = request.query_params.get("date_from")

        # Get queryset with filters for MacFossilFuel, Objective and Operation
        if self._execution_cache.get("objectives") is not None:
            objectives = self._execution_cache["objectives"]
        else:
            objectives = self.filter_queryset(self.get_queryset())
            if not objectives.exists():
                raise Http404("No objectives found.")
            else:
                self._execution_cache["objectives"] = objectives

        query_params = query_params or request.GET
        macs = MacFilter(query_params, queryset=MacFossilFuel.objects.all(), request=request).qs
        if not macs.exists():
            return

        operations_qs = Operation.objects.all()
        operations = OperationFilterForBalance(query_params, queryset=operations_qs, request=request).qs
        if not operations.exists():
            return

        # 1. Calculate "assiette" used for objectives calculation
        energy_basis = ObjectiveService.calculate_energy_basis(macs, objectives)

        # 2. Calculate the balances per category and sector
        balance_per_category, balance_per_sector = ObjectiveService.get_balances_for_objectives_calculation(
            operations, entity_id, date_from
        )

        # 3. Calculate the objectives per category and sector
        objective_per_category = ObjectiveService.calculate_objectives_and_penalties(
            balance_per_category,
            objectives,
            energy_basis,
            Objective.BIOFUEL_CATEGORY,
        )

        objective_per_sector = ObjectiveService.calculate_objectives_and_penalties(
            balance_per_sector,
            objectives,
            energy_basis,
            Objective.SECTOR,
        )

        # 4. Calculate the global objective
        global_objective_target, global_objective_penalty, global_objective_target_percent = (
            ObjectiveService.get_global_objective_and_penalty(objectives, energy_basis)
        )

        available_balance_sum = sum([sector["available_balance"] for sector in objective_per_sector])
        pending_teneur_sum = sum([sector["pending_teneur"] for sector in objective_per_sector])
        declared_teneur_sum = sum([sector["declared_teneur"] for sector in objective_per_sector])

        global_objective = {
            "available_balance": ObjectiveService.apply_ghg_conversion(available_balance_sum),
            "target": ObjectiveService.apply_ghg_conversion(global_objective_target),
            "pending_teneur": ObjectiveService.apply_ghg_conversion(pending_teneur_sum),
            "declared_teneur": ObjectiveService.apply_ghg_conversion(declared_teneur_sum),
            "unit": "tCO2",
            "target_percent": global_objective_target_percent,
        }
        penalty = ObjectiveService._calcule_penalty(
            global_objective_penalty,
            global_objective["pending_teneur"] + global_objective["declared_teneur"],
            global_objective["target"],
            tCO2=True,
        )

        global_objective["penalty"] = penalty

        # 5. Return the results
        result = {
            "main": global_objective,
            "sectors": objective_per_sector,
            "categories": objective_per_category,
        }

        return result
