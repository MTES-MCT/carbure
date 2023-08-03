import datetime

from django.http import JsonResponse
from core.decorators import check_admin_rights, check_rights
import pytz

from doublecount.models import (
    DoubleCountingApplication,
)
from doublecount.helpers import (
    send_dca_status_email,
)
from core.models import Entity, UserRights


@check_admin_rights()
def reject_dca(request, *args, **kwargs):
    dca_id = request.POST.get("dca_id", False)
    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)

    try:
        dca = DoubleCountingApplication.objects.get(id=dca_id)
    except:
        return JsonResponse({"status": "error", "message": "Could not find DCA"}, status=400)

    dca.status = DoubleCountingApplication.REJECTED
    send_dca_status_email(dca)
    dca.save()
    return JsonResponse({"status": "success"})
