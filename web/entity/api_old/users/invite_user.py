from django import forms
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods

from auth.views.mixins.register import send_email
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import UserRights, UserRightsRequests

User = get_user_model()


class InviteUserForm(forms.Form):
    email = forms.EmailField(required=True)
    role = forms.CharField(required=True)


class InviteUserError:
    INVALID_ROLE = "INVALID_ROLE"
    ACCESS_ALREADY_GIVEN = "ACCESS_ALREADY_GIVEN"
    INVITE_FAILED = "INVITE_FAILED"


@require_http_methods(["POST"])
@check_user_rights(role=[UserRights.ADMIN])
def invite_user(request, entity, entity_id):
    form = InviteUserForm(request.POST)

    if not form.is_valid():
        errors = dict(form.errors.items())
        return ErrorResponse(400, InviteUserError.INVITE_FAILED, data=errors)

    email = form.cleaned_data["email"]
    role = form.cleaned_data["role"]

    if role not in dict(UserRights.ROLES):
        return ErrorResponse(400, InviteUserError.INVALID_ROLE)

    email = User.objects.normalize_email(email)

    try:
        user = User.objects.get(email=email)

        email_subject = "Carbure - Invitation à rejoindre une entité"
        email_type = "invite_user_email"

    except Exception:
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
        UserRightsRequests.objects.update_or_create(user=user, entity=entity, defaults={"role": role, "status": "ACCEPTED"})
        UserRights.objects.create(user=user, entity=entity, role=role)

    except Exception:
        return ErrorResponse(400, InviteUserError.INVITE_FAILED)

    # Send email
    email_context = {"invitation": True, "entity_name": entity.name}
    send_email(user, request, email_subject, email_type, email_context)

    return SuccessResponse()
