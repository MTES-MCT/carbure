from os import environ

from django.conf import settings
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_otp import user_has_device
from django_otp.plugins.otp_email.models import EmailDevice

from auth.tokens import account_activation_token
from core.helpers import send_mail
from core.models import UserRights


def rotate_invited_activation_secret(user):
    """Replace the unusable password so previously issued activation links no longer match.

    Accounts that already chose a password are left untouched.
    """
    if user.has_usable_password():
        return
    user.set_unusable_password()
    user.save(update_fields=["password"])


def activation_email_context(user, entity_name=None):
    """Mark the activation mail as an invitation when the account still has no password."""
    if user.has_usable_password():
        return {}
    if not entity_name:
        rights = UserRights.objects.filter(user=user).select_related("entity").order_by("-date_added").first()
        entity_name = rights.entity.name if rights else ""
    return {"invitation": True, "entity_name": entity_name}


def send_email(user, request, subject, email_type, extra_context, rotate=False):
    if rotate:
        rotate_invited_activation_secret(user)
    email_subject = subject
    email_context = {
        "user": user,
        "domain": environ.get("BASE_URL"),
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
    } | extra_context
    html_message = loader.render_to_string(f"emails/{email_type}.html", email_context)
    text_message = loader.render_to_string(f"emails/{email_type}.txt", email_context)
    send_mail(
        request=request,
        subject=email_subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
        recipient_list=[user.email],
    )
    if not user_has_device(user):
        email_otp = EmailDevice()
        email_otp.user = user
        email_otp.name = "email"
        email_otp.confirmed = True
        email_otp.email = user.email
        email_otp.save()


def send_account_activation_email(user, request):
    send_email(
        user,
        request,
        "Carbure - Activation de compte",
        "account_activation_email",
        activation_email_context(user),
        rotate=True,
    )


def send_registration_email(user, entity_name, request, user_already_exists):
    """One activation mail when the account is created.

    A pending invite already has a link, so a later invitation only grants rights.
    An account that already has a password is told to sign in.
    """
    if user_already_exists and not user.has_usable_password():
        return
    if user_already_exists:
        send_email(
            user,
            request,
            "Carbure - Invitation à rejoindre une entité",
            "invite_user_email",
            {"entity_name": entity_name},
        )
        return
    send_email(
        user,
        request,
        "Carbure - Invitation à rejoindre une entité",
        "account_activation_email",
        activation_email_context(user, entity_name),
        rotate=True,
    )
