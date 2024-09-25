from django.db import transaction
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks
from core.carburetypes import CarbureError
from core.models import CarbureLot, CarbureLotEvent
from core.notifications import notify_correction_request, notify_lots_recalled
from transactions.helpers import check_locked_year


class RequestFixError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FROZEN_LOT = "FROZEN_LOT"
    UNAUTHORIZED_ENTITY = "UNAUTHORIZED_ENTITY"


class RequestFixSerializer(serializers.Serializer):
    # config fields
    lot_ids = serializers.PrimaryKeyRelatedField(queryset=CarbureLot.objects.all(), many=True)


class RequestFixMixin:
    @action(methods=["post"], detail=False, url_path="request-fix")
    def request_fix(self, request, *args, **kwargs):
        entity_id = request.query_params.get(
            "entity_id",
        )
        serializer = RequestFixSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lot_instances = serializer.validated_data["lot_ids"]

        lot_ids = [lot.id for lot in lot_instances]

        lots = CarbureLot.objects.filter(id__in=lot_ids)

        request_fix_events = []

        for lot in lots:
            if check_locked_year(lot.year):
                raise ValidationError({"message": CarbureError.YEAR_LOCKED})

            if lot.lot_status == CarbureLot.FROZEN:
                raise ValidationError({"message": RequestFixError.FROZEN_LOT})

            if lot.carbure_supplier_id == int(entity_id):
                event = CarbureLotEvent(event_type=CarbureLotEvent.RECALLED, lot=lot, user=request.user)
            elif lot.carbure_client_id == int(entity_id):
                event = CarbureLotEvent(event_type=CarbureLotEvent.FIX_REQUESTED, lot=lot, user=request.user)
            else:
                raise ValidationError({"message": RequestFixError.UNAUTHORIZED_ENTITY})

            request_fix_events.append(event)

        with transaction.atomic():
            lots.update(correction_status=CarbureLot.IN_CORRECTION)

            CarbureLotEvent.objects.bulk_create(request_fix_events)
            supplier_lots = lots.filter(carbure_supplier_id=entity_id).exclude(carbure_client_id=entity_id)
            notify_lots_recalled(supplier_lots)
            client_lots = lots.filter(carbure_client_id=entity_id).exclude(carbure_supplier_id=entity_id)
            notify_correction_request(client_lots)
            background_bulk_sanity_checks(lots)
        return Response({})
