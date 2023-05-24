import traceback

from django.http.response import JsonResponse
from core.decorators import check_user_rights

from core.models import (
    CarbureLot,
    GenericError,
)


@check_user_rights()
def toggle_warning(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_id = request.POST.get("lot_id")
    errors = request.POST.getlist("errors")
    checked = request.POST.get("checked") == "true"
    try:
        for error in errors:
            try:
                lot = CarbureLot.objects.get(id=lot_id)
                lot_error = GenericError.objects.get(lot_id=lot_id, error=error)
            except:
                traceback.print_exc()
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Could not locate wanted lot or error",
                    },
                    status=404,
                )
            # is creator
            if lot.added_by_id == int(entity_id):
                lot_error.acked_by_creator = checked
            # is recipient
            if lot.carbure_client_id == int(entity_id):
                lot_error.acked_by_recipient = checked
            lot_error.save()
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not update warning"}, status=500
        )
