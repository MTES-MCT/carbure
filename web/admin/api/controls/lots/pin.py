import traceback

from core.decorators import is_admin
from core.models import (
    CarbureLot,
)
from django.db.models import Case, Value, When
from django.http.response import JsonResponse


@is_admin
def toggle_pin(request, *args, **kwargs):
    selection = request.POST.getlist("selection", [])
    notify_auditor = request.POST.get("notify_auditor") == "true"
    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(
            highlighted_by_admin=Case(
                When(highlighted_by_admin=True, then=Value(False)),
                When(highlighted_by_admin=False, then=Value(True)),
            )
        )
        if notify_auditor:
            lots.update(highlighted_by_auditor=True)
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not pin lots"}, status=500
        )
