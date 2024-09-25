import traceback

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.helpers import get_stocks_summary_data


class SummaryMixin:
    @action(methods=["get"], detail=False)
    def summary(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        short = self.request.query_params.get("short", False)

        stock = self.filter_queryset(self.get_queryset())

        try:
            summary = get_stocks_summary_data(stock, entity_id, short == "true")
            return Response(summary)
        except Exception:
            traceback.print_exc()
            return Response(
                {"message": "Could not get stock summary"},
                status=status.HTTP_400_BAD_REQUEST,
            )
