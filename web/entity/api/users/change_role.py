from django.contrib.auth import get_user_model
from django import forms
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import UserRights, UserRightsRequests

User = get_user_model()


class ChangeRoleForm(forms.Form):
    email = forms.EmailField(required=True)
    role = forms.CharField(required=True)


class ChangeUserRoleError:
    MISSING_USER = "MISSING_USER"
    NO_PRIOR_RIGHTS = "NO_PRIOR_RIGHTS"
    UPDATE_FAILED = "UPDATE_FAILED"


@check_user_rights(role=[UserRights.ADMIN])
def change_user_role(request, entity, entity_id):
    form = ChangeRoleForm(request.POST)

    if not form.is_valid():
        errors = {key: e for key, e in form.errors.items()}
        return ErrorResponse(400, ChangeUserRoleError.UPDATE_FAILED, data=errors)

    email = form.cleaned_data["email"]
    role = form.cleaned_data["role"]

    try:
        user = User.objects.get(email=email)
    except:
        return ErrorResponse(400, ChangeUserRoleError.MISSING_USER)

    rights = UserRights.objects.filter(user=user, entity_id=entity_id).first()
    rights_request = UserRightsRequests.objects.filter(user=user, entity_id=entity_id).first()

    if not rights and not rights_request:
        return ErrorResponse(400, ChangeUserRoleError.NO_PRIOR_RIGHTS)

    try:
        if rights:
            rights.role = role
            rights.save()
        if rights_request:
            rights_request.role = role
            rights_request.save()
    except:
        return ErrorResponse(400, ChangeUserRoleError.UPDATE_FAILED)

    return SuccessResponse()
