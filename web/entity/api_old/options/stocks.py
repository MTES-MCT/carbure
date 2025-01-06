from django.http import JsonResponse

from core.decorators import check_user_rights
from core.models import CarbureStock, Entity, UserRights


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def toggle_stocks(request, *args, **kwargs):
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    has_stocks = request.POST.get("has_stocks", "false")
    if has_stocks == "false":
        stocks = CarbureStock.objects.filter(carbure_client=entity)
        if stocks.count() > 0:
            return JsonResponse({"status": "error", "message": "Cannot disable stocks if you have stocks"}, status=400)

    entity.has_stocks = True if has_stocks == "true" else False
    entity.save()
    return JsonResponse({"status": "success"})
