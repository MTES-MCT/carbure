from django.db.models.fields import NOT_PROVIDED

from django.http.response import JsonResponse
from core.decorators import check_user_rights
from core.helpers import (
    get_prefetched_data,
)
from transactions.sanity_checks.sanity_checks import bulk_scoring
from transactions.sanity_checks import (
    bulk_sanity_checks,
)

from core.models import (
    CarbureLot,
    Entity,
    UserRights,
)


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def duplicate_lot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_id = request.POST.get("lot_id", None)
    try:
        lot = CarbureLot.objects.get(id=lot_id)
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Unknown Lot %s" % (lot_id)}, status=400
        )

    if lot.added_by_id != int(entity_id):
        return JsonResponse(
            {"status": "forbidden", "message": "User not allowed"}, status=403
        )

    lot.pk = None
    lot.parent_stock = None
    lot.parent_lot = None
    lot_fields_to_remove = [
        "carbure_id",
        "correction_status",
        "lot_status",
        "delivery_status",
        "declared_by_supplier",
        "declared_by_client",
        "highlighted_by_admin",
        "highlighted_by_auditor",
    ]
    lot_meta_fields = {f.name: f for f in CarbureLot._meta.get_fields()}
    for f in lot_fields_to_remove:
        if f in lot_meta_fields:
            meta_field = lot_meta_fields[f]
            if meta_field.default != NOT_PROVIDED:
                setattr(lot, f, meta_field.default)
            else:
                setattr(lot, f, "")
    lot.save()
    data = get_prefetched_data(Entity.objects.get(id=entity_id))
    bulk_sanity_checks([lot], data)
    bulk_scoring([lot], data)
    return JsonResponse({"status": "success"})
