from django import forms

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights


class ToggleElecError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    NOT_OPERATOR = "NOT_OPERATOR"


class ToggleElecForm(forms.Form):
    entity_id = forms.IntegerField()
    has_elec = forms.BooleanField(required=False)


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def toggle_elec(request, *args, **kwargs):
    form = ToggleElecForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, ToggleElecError.MALFORMED_PARAMS, form.errors)

    entity_id = form.cleaned_data["entity_id"]
    has_elec = form.cleaned_data["has_elec"]

    entity = Entity.objects.get(id=entity_id)

    if entity.entity_type != Entity.OPERATOR:
        return ErrorResponse(400, ToggleElecError.NOT_OPERATOR)

    entity.has_elec = has_elec
    entity.save()

    return SuccessResponse()
