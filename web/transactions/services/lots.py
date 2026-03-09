from django.db import transaction

from carbure.tasks import background_bulk_scoring
from core.models import CarbureLotEvent
from core.serializers import CarbureLotPublicSerializer
from transactions.helpers import bulk_insert_lots, construct_carbure_lot
from transactions.sanity_checks.helpers import get_prefetched_data


class LotCreationFailure(RuntimeError):
    pass


def create_lot(user, entity, source, lot_data):
    d = get_prefetched_data(entity)
    lot, errors = construct_carbure_lot(d, entity, lot_data)

    if not lot:
        raise LotCreationFailure()

    with transaction.atomic():
        lots_created = bulk_insert_lots(entity, [lot], [errors], d)

        if len(lots_created) == 0:
            raise LotCreationFailure()

        background_bulk_scoring(lots_created)

        CarbureLotEvent.objects.create(
            event_type=CarbureLotEvent.CREATED,
            lot_id=lots_created[0].id,
            user=user,
            metadata={"source": source},
            entity=entity,
        )

    return CarbureLotPublicSerializer(lots_created[0]).data
