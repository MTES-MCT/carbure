from os import environ

from django.conf import settings
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_otp import user_has_device
from django_otp.plugins.otp_email.models import EmailDevice

from auth.tokens import account_activation_token
from core.helpers import send_mail


def send_email(user, request, subject, email_type, extra_context):
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
    send_email(user, request, "Carbure - Activation de compte", "account_activation_email", {})


def send_registration_email(user, entity_name, request, user_already_exists):
    email_context = {"invitation": True, "entity_name": entity_name}
    email_type = "invite_user_email" if user_already_exists else "account_activation_email"
    send_email(user, request, "Carbure - Invitation à rejoindre une entité", email_type, email_context)
