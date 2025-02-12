from drf_spectacular.utils import OpenApiExample, OpenApiTypes, extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse
from core.models import Entity
from saf.serializers.saf_ticket import export_tickets_to_excel


class ExportActionMixin:
    @extend_schema(
        filters=True,
        examples=[
            OpenApiExample(
                "Example of export response.",
                value="csv file.csv",
                request_only=False,
                response_only=True,
                media_type="application/vnd.ms-excel",
            ),
        ],
        responses={
            (200, "application/vnd.ms-excel"): OpenApiTypes.STR,
        },
    )
    @action(methods=["get"], detail=False)
    def export(self, request, *args, **kwargs):
        entity = Entity.objects.get(pk=request.query_params.get("entity_id"))
        tickets = self.filter_queryset(self.get_queryset())
        file = export_tickets_to_excel(tickets, entity)
        return ExcelResponse(file)
