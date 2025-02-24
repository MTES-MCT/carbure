from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.serializers.teneur import (
    SimulationInputSerializer,
    SimulationMinMaxInputSerializer,
    SimulationMinMaxOutputSerializer,
    SimulationOutputSerializer,
)
from tiruert.services.teneur import TeneurService


class SimulateActionMixin:
    @extend_schema(
        operation_id="simulate",
        description="Simulate a blending operation",
        request=SimulationInputSerializer,
        responses={status.HTTP_200_OK: SimulationOutputSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
    )
    def simulate(self, request):
        input_serializer_class = SimulationInputSerializer
        output_serializer_class = SimulationOutputSerializer

        serializer = input_serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            try:
                selected_lots, lot_ids, emissions, fun = TeneurService.prepare_data_and_optimize(
                    data["debited_entity"].id,
                    data,
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            detail_operations_data = []
            for idx, lot_volume in selected_lots.items():
                detail_operations_data.append(
                    {
                        "lot_id": lot_ids[idx],
                        "volume": lot_volume,
                        "emission_rate_per_mj": emissions[idx],
                    }
                )
            result_data = {"selected_lots": detail_operations_data, "fun": fun}

            output_serializer = output_serializer_class(result_data, many=False)
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="simulation_bounds",
        description="Get bounds for blending operation",
        request=SimulationMinMaxInputSerializer,
        responses={status.HTTP_200_OK: SimulationOutputSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="simulate/min_max",
    )
    def simulate_min_max(self, request):
        input_serializer_class = SimulationMinMaxInputSerializer
        output_serializer_class = SimulationMinMaxOutputSerializer

        serializer = input_serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            try:
                min, max = TeneurService.get_min_and_max_emissions(
                    data["debited_entity"].id,
                    data,
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            output_serializer = output_serializer_class(
                {
                    "min_avoided_emissions": min,  # tCO2
                    "max_avoided_emissions": max,  # tCO2
                }
            )
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
