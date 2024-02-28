import traceback
from django.db.models import Case, Value, When

from django.http.response import JsonResponse

from core.decorators import check_user_rights, is_auditor

from core.models import (
    CarbureLot,
)


@check_user_rights()
@is_auditor
def toggle_pin(request, *args, **kwargs):
    selection = request.POST.getlist("selection", [])
    notify_admin = request.POST.get("notify_admin") == "true"
    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(
            highlighted_by_auditor=Case(
                When(highlighted_by_auditor=True, then=Value(False)),
                When(highlighted_by_auditor=False, then=Value(True)),
            )
        )
        if notify_admin:
            lots.update(highlighted_by_admin=True)
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not pin lots"}, status=500
        )
