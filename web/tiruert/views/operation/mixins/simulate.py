from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.serializers.operation import OperationInputSerializer
from tiruert.serializers.teneur import SimulationInputSerializer, SimulationOutputSerializer
from tiruert.services.teneur import TeneurService


class SimulateActionMixin:
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

            operations = (
                self.get_queryset()
                .filter(
                    biofuel=data["biofuel"],
                    customs_category=data["customs_category"],
                    # created_at__gte=data["date_from"],
                )
                .filter((Q(credited_entity=data["debited_entity"]) | Q(debited_entity=data["debited_entity"])))
                .distinct()
            )

            selected_lots, lot_ids, emissions, volumes = TeneurService.prepare_data_and_optimize(
                operations, data["debited_entity"].id, data
            )
            if not selected_lots:
                return serializer.ValidationError(OperationInputSerializer.NO_SUITABLE_LOTS_FOUND)

            detail_operations_data = []
            for idx, lot_volume in selected_lots.items():
                detail_operations_data.append(
                    {
                        "lot_id": lot_ids[idx],
                        "volume": lot_volume,
                        "saved_ghg": emissions[idx] * lot_volume / volumes[idx],
                    }
                )

            output_serializer = output_serializer_class(detail_operations_data, many=True)
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
