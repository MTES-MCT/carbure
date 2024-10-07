from authtools.forms import UserCreationForm
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_otp import user_has_device
from django_otp.plugins.otp_email.models import EmailDevice

from auth.tokens import account_activation_token
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.helpers import send_mail


def register(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        # Send email
        subject = "Carbure - Activation de compte"
        send_email(user, request, subject)
        return SuccessResponse()
    else:
        errors = dict(form.errors.items())
        # return JsonResponse({'status': 'error', 'message': 'Invalid Form', 'errors': errors}, status=400)
        return ErrorResponse(400, CarbureError.INVALID_REGISTRATION_FORM, data=errors)


def send_email(user, request, subject, email_type="account_activation_email", extra_context=None):
    if extra_context is None:
        extra_context = {}
    current_site = get_current_site(request)
    email_subject = subject
    email_context = {
        "user": user,
        "domain": current_site.domain,
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
