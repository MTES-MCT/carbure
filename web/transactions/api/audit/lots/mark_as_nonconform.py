import traceback
from django.http.response import JsonResponse
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import CarbureLot, Entity


@check_user_rights(entity_type=[Entity.AUDITOR])
def mark_nonconform(request):
    selection = request.POST.getlist("selection", [])
    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(audit_status=CarbureLot.NONCONFORM)
        return SuccessResponse()
    except:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not mark lots as conform"}, status=500)
