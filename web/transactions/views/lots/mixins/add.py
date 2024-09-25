from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_scoring
from core.models import CarbureLotEvent, Entity
from core.serializers import CarbureLotPublicSerializer
from transactions.helpers import bulk_insert_lots, construct_carbure_lot
from transactions.sanity_checks.helpers import get_prefetched_data


class AddLotError:
    LOT_CREATION_FAILED = ("LOT_CREATION_FAILED", _("Le lot n'a pas pu être créé."))


class AddMixin:
    @action(methods=["post"], detail=False)
    def add(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)

        d = get_prefetched_data(entity)
        lot_data = request.data
        lot, errors = construct_carbure_lot(d, entity, lot_data)
        if not lot:
            raise ValidationError({"message": AddLotError.LOT_CREATION_FAILED})

        # run sanity checks, insert lot and errors
        with transaction.atomic():
            lots_created = bulk_insert_lots(entity, [lot], [errors], d)

            if len(lots_created) == 0:
                raise ValidationError({"message": AddLotError.LOT_CREATION_FAILED})

            background_bulk_scoring(lots_created)

            CarbureLotEvent.objects.create(
                event_type=CarbureLotEvent.CREATED,
                lot_id=lots_created[0].id,
                user=request.user,
                metadata={"source": "MANUAL"},
            )

        data = CarbureLotPublicSerializer(lots_created[0]).data
        return Response(data)
