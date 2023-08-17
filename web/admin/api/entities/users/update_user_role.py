from django import forms
from django.db import transaction
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights, UserRights


class UpdateRoleErrors:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    RIGHTS_NOT_FOUND = "RIGHTS_NOT_FOUND"


class UpdateRoleForm(forms.Form):
    request_id = forms.IntegerField()
    role = forms.CharField()


@check_admin_rights(allow_external=[ExternalAdminRights.AIRLINE])
def update_user_role(request):
    form = UpdateRoleForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, UpdateRoleErrors.MALFORMED_PARAMS, form.errors)

    request_id = form.cleaned_data["request_id"]
    role = form.cleaned_data["role"]

    try:
        rights = UserRights.objects.get(id=request_id)
    except:
        return ErrorResponse(400, UpdateRoleErrors.RIGHTS_NOT_FOUND)

    with transaction.atomic():
        rights.role = role
        rights.save()

    return SuccessResponse()
