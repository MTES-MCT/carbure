from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.serializers import DebtSummarySerializer
from tiruert.serializers.debt import DebtRepaymentSimulationInputSerializer, DebtRepaymentSimulationSerializer
from tiruert.services.debt import DebtService
from tiruert.services.operation import OperationService


class DebtActionMixin:
    @extend_schema(
        operation_id="list_debts",
        description="Remaining debt volume of the entity per biofuel and customs category",
        responses={status.HTTP_200_OK: DebtSummarySerializer(many=True)},
    )
    @action(detail=False, methods=["get"], pagination_class=None, filterset_class=None, filter_backends=[])
    def debts(self, request):
        summary = DebtService.summarize_open_debts(request.entity.id)
        return Response(DebtSummarySerializer(summary, many=True).data)

    @extend_schema(
        operation_id="simulate_debt_repayment",
        request=DebtRepaymentSimulationInputSerializer,
        responses={status.HTTP_200_OK: DebtRepaymentSimulationSerializer},
    )
    @action(detail=False, methods=["post"], filterset_class=None, filter_backends=[])
    def simulate_debt_repayment(self, request):
        serializer = DebtRepaymentSimulationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        OperationService.check_debited_entity(request.entity.id, data)
        result = DebtService.simulate_tco2_repayment(data)
        return Response(DebtRepaymentSimulationSerializer(result).data)
