import traceback

from django.http.response import JsonResponse

from core.decorators import check_user_rights, is_auditor

from core.models import (
    GenericError,
)


@check_user_rights()
@is_auditor
def toggle_warning(request, *args, **kwargs):
    lot_id = request.POST.get("lot_id")
    errors = request.POST.getlist("errors")
    checked = request.POST.get("checked") == "true"
    try:
        for error in errors:
            try:
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
            lot_error.acked_by_auditor = checked
            lot_error.save()
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not update warning"}, status=500
        )
