from django import forms
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models import ElecChargePoint
from elec.serializers.elec_charge_point import ElecChargePointSerializer


class ChargePointDetailForm(forms.Form):
    charge_point_id = forms.ModelChoiceField(queryset=ElecChargePoint.objects.filter(is_deleted=False))


class ChargePointDetailError:
    CP_NOT_FOUND_ON_CPO = "CP_NOT_FOUND_ON_CPO"


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_charge_point_details(request, entity, entity_id):
    form = ChargePointDetailForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    cp = form.cleaned_data["charge_point_id"]

    if cp.cpo != entity:
        return ErrorResponse(400, ChargePointDetailError.CP_NOT_FOUND_ON_CPO)

    serialized = ElecChargePointSerializer(cp).data
    return SuccessResponse(serialized)
