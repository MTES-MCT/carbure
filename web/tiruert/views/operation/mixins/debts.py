from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.serializers import DebtSummarySerializer
from tiruert.services.debt import DebtService


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
