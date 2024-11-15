from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.decorators import action

from core.models import Entity
from core.xlsx_v3 import export_carbure_lots


class ExportMixin:
    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
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
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        lots = self.filter_queryset(self.get_queryset())
        file_location = export_carbure_lots(entity, lots)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (file_location)
        return response
