import traceback

from django.http.response import JsonResponse

from core.common import SuccessResponse
from core.decorators import check_user_rights, is_auditor

from core.models import (
    CarbureLot,
)


@check_user_rights()
@is_auditor
def mark_nonconform(request, *args, **kwargs):
    selection = request.POST.getlist("selection", [])
    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(audit_status=CarbureLot.NONCONFORM)
        return SuccessResponse()
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not mark lots as conform"}, status=500
        )
