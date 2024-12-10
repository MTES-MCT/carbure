from datetime import datetime

from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.decorators import action

from .utils import export_agreements


class ExportActionMixin:
    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
            OpenApiParameter(
                "year",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Year",
                required=False,
            ),
        ],
        examples=[
            OpenApiExample(
                "Example of export response.",
                value="csv file.csv",
                request_only=False,
                response_only=True,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        ],
        responses={
            (
                200,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ): OpenApiTypes.STR,
        },
    )
    @action(methods=["get"], detail=False)
    def export(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        year = self.request.query_params.get("year", datetime.now().year)

        agreements_active = (
            queryset.filter(Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year))
            .select_related("production_site")
            .order_by("production_site__name")
        )

        file_location = export_agreements(agreements_active)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (file_location)
        return response
