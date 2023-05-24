from core.models import CarbureLotEvent, Entity, UserRights
from core.decorators import check_user_rights
from core.helpers import get_prefetched_data
from transactions.helpers import construct_carbure_lot, bulk_insert_lots
from django.http.response import JsonResponse
from carbure.tasks import background_bulk_scoring
from core.serializers import CarbureLotPublicSerializer


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_lot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    entity = Entity.objects.get(pk=entity_id)

    d = get_prefetched_data(entity)
    lot_obj, errors = construct_carbure_lot(d, entity, request.POST.dict())
    if not lot_obj:
        return JsonResponse(
            {"status": "error", "message": "Something went wrong"}, status=400
        )

    # run sanity checks, insert lot and errors
    lots_created = bulk_insert_lots(entity, [lot_obj], [errors], d)
    if len(lots_created) == 0:
        return JsonResponse(
            {"status": "error", "message": "Something went wrong"}, status=500
        )
    background_bulk_scoring(lots_created)
    e = CarbureLotEvent()
    e.event_type = CarbureLotEvent.CREATED
    e.lot_id = lots_created[0].id
    e.user = request.user
    e.metadata = {"source": "MANUAL"}
    e.save()

    data = CarbureLotPublicSerializer(e.lot).data
    return JsonResponse({"status": "success", "data": data})
