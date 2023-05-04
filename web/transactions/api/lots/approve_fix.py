from django import forms
from django.db import transaction

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from core.models import UserRights, CarbureLot, CarbureLotEvent


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

    approve_fix_events = []

    for lot in lots:
        if lot.carbure_client_id != entity_id:
            return ErrorResponse(400, ApproveFixError.UNAUTHORIZED_ENTITY)

        event = CarbureLotEvent(event_type=CarbureLotEvent.FIX_ACCEPTED, lot=lot, user=request.user)
        approve_fix_events.append(event)

    with transaction.atomic():
        lots.update(correction_status=CarbureLot.NO_PROBLEMO)
        CarbureLotEvent.objects.bulk_create(approve_fix_events)

    return SuccessResponse()


class ApproveFixForm(forms.Form):
    # choices
    LOTS = CarbureLot.objects.all()

    # config fields
    entity_id = forms.IntegerField()
    lot_ids = forms.ModelMultipleChoiceField(queryset=LOTS)
