from django import forms
from django.db import transaction

from carbure.tasks import background_bulk_sanity_checks
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import CarbureLot, CarbureLotEvent, UserRights
from core.notifications import notify_correction_request, notify_lots_recalled
from transactions.helpers import check_locked_year


class RequestFixError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FROZEN_LOT = "FROZEN_LOT"
    UNAUTHORIZED_ENTITY = "UNAUTHORIZED_ENTITY"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def request_fix(request, context):
    form = RequestFixForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, RequestFixError.MALFORMED_PARAMS, form.errors)

    entity_id = form.cleaned_data["entity_id"]
    lots = form.cleaned_data["lot_ids"]
    request_fix_events = []

    for lot in lots:
        if check_locked_year(lot.year):
            return ErrorResponse(400, CarbureError.YEAR_LOCKED)

        if lot.lot_status == CarbureLot.FROZEN:
            return ErrorResponse(400, RequestFixError.FROZEN_LOT)

        if lot.carbure_supplier_id == entity_id:
            event = CarbureLotEvent(event_type=CarbureLotEvent.RECALLED, lot=lot, user=request.user)
        elif lot.carbure_client_id == entity_id:
            event = CarbureLotEvent(event_type=CarbureLotEvent.FIX_REQUESTED, lot=lot, user=request.user)
        else:
            return ErrorResponse(400, RequestFixError.UNAUTHORIZED_ENTITY)

        request_fix_events.append(event)

    with transaction.atomic():
        lots.update(correction_status=CarbureLot.IN_CORRECTION)
        CarbureLotEvent.objects.bulk_create(request_fix_events)

        supplier_lots = lots.filter(carbure_supplier_id=entity_id).exclude(carbure_client_id=entity_id)
        notify_lots_recalled(supplier_lots)

        client_lots = lots.filter(carbure_client_id=entity_id).exclude(carbure_supplier_id=entity_id)
        notify_correction_request(client_lots)

        background_bulk_sanity_checks(lots)

    return SuccessResponse()


class RequestFixForm(forms.Form):
    # choices
    LOTS = CarbureLot.objects.all()

    # config fields
    entity_id = forms.IntegerField()
    lot_ids = forms.ModelMultipleChoiceField(queryset=LOTS)
