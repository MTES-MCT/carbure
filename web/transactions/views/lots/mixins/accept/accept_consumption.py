from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent


class AcceptConsumptionError:
    VALIDATION_FAILED = "VALIDATION_FAILED"
    NOT_CLIENT = "NOT_CLIENT"
    INVALID_STATUS = "INVALID_STATUS"


class AcceptConsumptionMixin:
    @action(methods=["post"], detail=False, url_path="accept-consumption")
    def accept_consumption(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        lots = self.filter_queryset(self.get_queryset())
        # TODO: fix, required ?
        selection = request.data.getlist("selection")
        if len(selection) > 0:
            lots = lots.filter(pk__in=selection)

        updated_lots = []
        accepted_events = []
        errors = []
        for lot in lots:
            if int(entity_id) != lot.carbure_client_id:
                errors.append(
                    {
                        "error": AcceptConsumptionError.NOT_CLIENT,
                        "meta": {"lot_id": lot.id},
                    }
                )
                continue

            if lot.lot_status != CarbureLot.PENDING:
                errors.append(
                    {
                        "error": AcceptConsumptionError.INVALID_STATUS,
                        "meta": {"lot_id": lot.id, "status": lot.lot_status},
                    }
                )
                continue

            lot.lot_status = CarbureLot.ACCEPTED
            lot.delivery_type = CarbureLot.CONSUMPTION
            updated_lots.append(lot)

            event = CarbureLotEvent(event_type=CarbureLotEvent.ACCEPTED, lot=lot, user=request.user)
            accepted_events.append(event)

        if len(errors) > 0:
            raise ValidationError({"message": AcceptConsumptionError.VALIDATION_FAILED, "errors": errors})

        with transaction.atomic():
            CarbureLot.objects.bulk_update(updated_lots, ["lot_status", "delivery_type"])
            CarbureLotEvent.objects.bulk_create(accepted_events)

        return Response({"status": "success"})
