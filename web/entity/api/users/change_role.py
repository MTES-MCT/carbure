from django.contrib.auth import get_user_model
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import UserRights

User = get_user_model()


class ChangeUserRoleError:
    MISSING_PARAMS = "MISSING_PARAMS"
    MISSING_USER = "MISSING_USER"
    NO_PRIOR_RIGHTS = "NO_PRIOR_RIGHTS"
    UPDATE_FAILED = "UPDATE_FAILED"


@check_user_rights(role=[UserRights.ADMIN])
def change_user_role(request, *args, **kwargs):
    entity_id = request.POST.get("entity_id")
    email = request.POST.get("email")
    role = request.POST.get("role")

    if not email or not role:
        return ErrorResponse(400, ChangeUserRoleError.MISSING_PARAMS)

    try:
        user = User.objects.get(email=email)
    except:
        return ErrorResponse(400, ChangeUserRoleError.MISSING_USER)

    rights = UserRights.objects.filter(user=user, entity_id=entity_id).first()

    if not rights:
        return ErrorResponse(400, ChangeUserRoleError.NO_PRIOR_RIGHTS)

    try:
        rights.role = role
        rights.save()
    except:
        return ErrorResponse(400, ChangeUserRoleError.UPDATE_FAILED)

    return SuccessResponse()
