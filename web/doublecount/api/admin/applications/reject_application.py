from django.http import JsonResponse

from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from doublecount.models import (
    DoubleCountingApplication,
)


@check_admin_rights(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])
def reject_dca(request, *args, **kwargs):
    dca_id = request.POST.get("dca_id", False)
    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)

    try:
        dca = DoubleCountingApplication.objects.get(id=dca_id)
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find DCA"}, status=400)

    dca.status = DoubleCountingApplication.REJECTED
    # send_dca_status_email(dca, request) TODO: uncomment when email is ready
    dca.save()
    return JsonResponse({"status": "success"})
