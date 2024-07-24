from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import UserRights, UserRightsRequests, Entity
from auth.api.register import send_email as send_registration_email

User = get_user_model()


class InviteUserError:
    MISSING_PARAMS = "MISSING_PARAMS"
    INVALID_ROLE = "INVALID_ROLE"
    INVALID_ENTITY = "INVALID_ENTITY"
    ACCESS_ALREADY_GIVEN = "ACCESS_ALREADY_GIVEN"
    INVITE_FAILED = "INVITE_FAILED"


@require_http_methods(["POST"])
@check_user_rights(role=[UserRights.ADMIN])
def invite_user(request, *args, **kwargs):
    entity_id = request.POST.get("entity_id")
    email = request.POST.get("email")
    role = request.POST.get("role")

    if not entity_id or not email or not role:
        return ErrorResponse(400, InviteUserError.MISSING_PARAMS)

    if role not in dict(UserRights.ROLES):
        return ErrorResponse(400, InviteUserError.INVALID_ROLE)

    entity = Entity.objects.get(id=entity_id)
    if not entity:
        return ErrorResponse(400, InviteUserError.INVALID_ENTITY)

    email = User.objects.normalize_email(email)

    try:
        user = User.objects.get(email=email)

        email_subject = "Carbure - Invitation à rejoindre une entité"
        email_type = "invite_user_email"

    except:
        # Create a new user (non active) with a random password
        user = User.objects.create_user(email=email, password=User.objects.make_random_password(20), is_active=False)
        user.save()

        email_subject = "Carbure - Invitation à rejoindre une entité"
        email_type = "account_activation_email"

    # Update rights and requests
    check_user_rights = UserRights.objects.filter(user=user, entity=entity).first()
    if check_user_rights:
        return ErrorResponse(400, InviteUserError.ACCESS_ALREADY_GIVEN)

    try:
        UserRightsRequests.objects.update_or_create(user=user, entity=entity, role=role, status="ACCEPTED")
        UserRights.objects.update_or_create(user=user, entity=entity, role=role)

    except:
        return ErrorResponse(400, InviteUserError.INVITE_FAILED)

    # Send email
    email_context = {"invitation": True, "entity_name": entity.name}
    send_registration_email(user, request, email_subject, email_type, email_context)

    return SuccessResponse()
