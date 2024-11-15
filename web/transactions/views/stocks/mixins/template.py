from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from core.xlsx_v3 import template_v4_stocks


class TemplateMixin:
    @extend_schema(
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
                "Example of response.",
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
    def template(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        entity = get_object_or_404(Entity, id=entity_id)
        file_location = template_v4_stocks(entity)
        try:
            with open(file_location, "rb") as f:
                file_data = f.read()
                # sending response
                response = HttpResponse(file_data, content_type="application/vnd.ms-excel")
                response["Content-Disposition"] = 'attachment; filename="carbure_template_stocks.xlsx"'
                return response
        except Exception:
            return Response(
                {"message": "Error creating template file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
