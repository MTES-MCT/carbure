from django.http.response import HttpResponse, JsonResponse

from core.decorators import check_user_rights
from core.models import (
    Entity,
)
from core.xlsx_v3 import template_v4, template_v4_stocks


@check_user_rights()
def get_template(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    file_location = template_v4(entity)
    try:
        with open(file_location, "rb") as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type="application/vnd.ms-excel")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="carbure_template.xlsx"'
            return response
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Error creating template file"}, status=500
        )


@check_user_rights()
def get_template_stock(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    file_location = template_v4_stocks(entity)
    try:
        with open(file_location, "rb") as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type="application/vnd.ms-excel")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="carbure_template_stocks.xlsx"'
            return response
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Error creating template file"}, status=500
        )
