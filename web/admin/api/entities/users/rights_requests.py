from core.decorators import check_admin_rights
from django.http import JsonResponse
from django.db.models import Q
from core.models import ExternalAdminRights

from core.models import UserRights


@check_admin_rights(allow_external=[ExternalAdminRights.AIRLINE])
def get_rights_requests(request):
    q = request.GET.get("q", False)
    statuses = request.GET.getlist("statuses", False)
    company_id = request.GET.get("company_id", False)
    rights = UserRights.objects.all()

    if company_id:
        rights = rights.filter(entity__id=company_id)
    if statuses:
        rights = rights.filter(status__in=statuses)
    if q:
        rights = rights.filter(Q(user__email__icontains=q) | Q(entity__name__icontains=q))

    requests_sez = [r.natural_key() for r in rights]
    return JsonResponse({"status": "success", "data": requests_sez})
