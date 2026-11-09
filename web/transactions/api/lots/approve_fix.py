from django import forms
from django.db import transaction

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import CarbureLot, CarbureLotEvent, UserRights
from tiruert.services.correction import CorrectionService


class ApproveFixError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    UNAUTHORIZED_ENTITY = "UNAUTHORIZED_ENTITY"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def approve_fix(request, context):
    form = ApproveFixForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, ApproveFixError.MALFORMED_PARAMS, form.errors)

    entity_id = form.cleaned_data["entity_id"]
    lots = form.cleaned_data["lot_ids"]
    lot_ids = []

    approve_fix_events = []

    for lot in lots:
        lot_ids.append(lot.id)
        if lot.carbure_client_id != entity_id:
            return ErrorResponse(400, ApproveFixError.UNAUTHORIZED_ENTITY)

        event = CarbureLotEvent(event_type=CarbureLotEvent.FIX_ACCEPTED, lot=lot, user=request.user, entity_id=entity_id)
        approve_fix_events.append(event)

    with transaction.atomic():
        locked_lots = CarbureLot.objects.select_for_update().filter(id__in=lot_ids).order_by("id")
        fixed_lot_ids = [lot.id for lot in locked_lots if lot.correction_status == CarbureLot.FIXED]
        lots.update(correction_status=CarbureLot.NO_PROBLEMO)
        if fixed_lot_ids:
            CorrectionService.create_correction_operations_for_lot_volume_update(sorted(fixed_lot_ids))
        CarbureLotEvent.objects.bulk_create(approve_fix_events)

    return SuccessResponse()


class ApproveFixForm(forms.Form):
    # choices
    LOTS = CarbureLot.objects.all()

    # config fields
    entity_id = forms.IntegerField()
    lot_ids = forms.ModelMultipleChoiceField(queryset=LOTS)
