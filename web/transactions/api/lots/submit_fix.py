from django import forms
from django.db import transaction
from django.db.models import Q

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from core.models import UserRights, CarbureLot, CarbureLotEvent
from core.notifications import notify_correction_done
from core.traceability import get_traceability_nodes, bulk_update_traceability_nodes


class SubmitFixError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FROZEN_LOT = "FROZEN_LOT"
    UNAUTHORIZED_ENTITY = "UNAUTHORIZED_ENTITY"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def submit_fix(request, context):
    form = SubmitFixForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, SubmitFixError.MALFORMED_PARAMS, form.errors)

    entity_id = form.cleaned_data["entity_id"]
    lots = form.cleaned_data["lot_ids"]

    submit_fix_events = []

    for lot in lots:
        if lot.lot_status == CarbureLot.FROZEN:
            return ErrorResponse(400, SubmitFixError.FROZEN_LOT)

        if lot.added_by_id != entity_id:
            return ErrorResponse(400, SubmitFixError.UNAUTHORIZED_ENTITY)

        event = CarbureLotEvent(event_type=CarbureLotEvent.MARKED_AS_FIXED, lot=lot, user=request.user)
        submit_fix_events.append(event)

    rejected_lots = lots.filter(lot_status=CarbureLot.REJECTED)
    fix_lots = lots.filter(correction_status=CarbureLot.IN_CORRECTION)
    own_lots = lots.filter(added_by_id=entity_id).filter(Q(carbure_client_id=entity_id) | Q(carbure_client_id=None))

    # query the database for all the traceability nodes related to these lots
    nodes = get_traceability_nodes(fix_lots)

    updated_nodes = []
    for node in nodes:
        # propagate the corrections to any other connected model
        updated_nodes += node.propagate()

    with transaction.atomic():
        rejected_lots.update(lot_status=CarbureLot.PENDING, correction_status=CarbureLot.NO_PROBLEMO)
        fix_lots.update(correction_status=CarbureLot.FIXED)
        own_lots.update(correction_status=CarbureLot.NO_PROBLEMO)

        bulk_update_traceability_nodes(updated_nodes)

        CarbureLotEvent.objects.bulk_create(submit_fix_events)
        notify_correction_done(lots.exclude(carbure_client_id=entity_id))

    return SuccessResponse()


class SubmitFixForm(forms.Form):
    # choices
    LOTS = CarbureLot.objects.all()

    # config fields
    entity_id = forms.IntegerField()
    lot_ids = forms.ModelMultipleChoiceField(queryset=LOTS)
