from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.serializers import DebtRepaymentInputSerializer, DebtSummarySerializer, OperationListSerializer
from tiruert.services.debt import DebtService


class RepayDebtActionMixin:
    @extend_schema(
        operation_id="repay_debt",
        description="Repay the open debts of a biofuel / customs category by debiting lots of the entity",
        request=DebtRepaymentInputSerializer,
        responses={status.HTTP_201_CREATED: OperationListSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], pagination_class=None, filterset_class=None, filter_backends=[])
    def repay_debt(self, request):
        serializer = DebtRepaymentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        operations = DebtService.repay(
            request.entity, data["biofuel"], data["customs_category"], data["lots"], status=data["status"]
        )

        # Re-read through the viewset queryset to get the annotations the list serializer relies on
        created = self.get_queryset().filter(id__in=[operation.id for operation in operations]).order_by("id")
        return Response(OperationListSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="list_debts",
        description="Remaining debt volume of the entity per biofuel and customs category",
        responses={status.HTTP_200_OK: DebtSummarySerializer(many=True)},
    )
    @action(detail=False, methods=["get"], pagination_class=None, filterset_class=None, filter_backends=[])
    def debts(self, request):
        summary = DebtService.summarize_open_debts(request.entity.id)
        return Response(DebtSummarySerializer(summary, many=True).data)
