from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from core.xlsx_v3 import template_v4


class TemplateMixin:
    @action(methods=["get"], detail=False)
    def template(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        entity = get_object_or_404(Entity, id=entity_id)
        file_location = template_v4(entity)
        try:
            with open(file_location, "rb") as f:
                file_data = f.read()
                # sending response
                response = HttpResponse(file_data, content_type="application/vnd.ms-excel")
                response["Content-Disposition"] = 'attachment; filename="carbure_template.xlsx"'
                return response
        except Exception:
            return Response(
                {"message": "Error creating template file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
