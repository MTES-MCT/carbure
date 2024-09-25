import traceback

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.helpers import get_lots_summary_data
from core.models import Entity


class SummaryMixin:
    @action(methods=["get"], detail=False)
    def summary(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        short = self.request.query_params.get("short", False)
        query_status = self.request.query_params.get("status", False)

        entity = get_object_or_404(Entity, id=entity_id)

        mutable_params = request.GET.copy()
        mutable_params["will_aggregate"] = "true"
        request.GET = mutable_params

        lots = self.filter_queryset(self.get_queryset())

        if not query_status:
            raise ValidationError({"message": "Missing status"})
        try:
            entity = Entity.objects.get(id=entity_id)
            summary = get_lots_summary_data(lots, entity, short)
            return Response(summary)
        except Exception:
            traceback.print_exc()
            return Response(
                {"status": "error", "message": "Could not get lots summary"},
                status=status.HTTP_400_BAD_REQUEST,
            )
