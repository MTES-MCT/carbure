from django.db import transaction
from django.utils.translation import gettext as _

from core.common import ErrorResponse, SuccessResponse
from core.models import CarbureLotEvent, UserRights
from core.decorators import check_user_rights
from transactions.sanity_checks.helpers import get_prefetched_data
from transactions.helpers import construct_carbure_lot, bulk_insert_lots
from carbure.tasks import background_bulk_scoring
from core.serializers import CarbureLotPublicSerializer


class AddLotError:
    LOT_CREATION_FAILED = ("LOT_CREATION_FAILED", _("Le lot n'a pas pu être créé."))


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_lot(request, entity):
    d = get_prefetched_data(entity)
    lot_data = request.POST.dict()

    lot, errors = construct_carbure_lot(d, entity, lot_data)
    if not lot:
        return ErrorResponse(400, AddLotError.LOT_CREATION_FAILED)

    # run sanity checks, insert lot and errors
    with transaction.atomic():
        lots_created = bulk_insert_lots(entity, [lot], [errors], d)

        if len(lots_created) == 0:
            return ErrorResponse(400, AddLotError.LOT_CREATION_FAILED)

        background_bulk_scoring(lots_created)

        CarbureLotEvent.objects.create(
            event_type=CarbureLotEvent.CREATED,
            lot_id=lots_created[0].id,
            user=request.user,
            metadata={"source": "MANUAL"},
        )

    data = CarbureLotPublicSerializer(lots_created[0]).data
    return SuccessResponse(data)
