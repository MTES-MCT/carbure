from auth.tokens import account_activation_token
from authtools.forms import UserCreationForm
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_otp.plugins.otp_email.models import EmailDevice


def register(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(request)
        # send email
        email_subject = "Carbure - Activation de compte"
        email_context = {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        }
        html_message = loader.render_to_string("emails/account_activation_email.html", email_context)
        text_message = loader.render_to_string("emails/account_activation_email.txt", email_context)
        send_mail(
            subject=email_subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            html_message=html_message,
            recipient_list=[user.email],
            fail_silently=False,
        )
        email_otp = EmailDevice()
        email_otp.user = user
        email_otp.name = "email"
        email_otp.confirmed = True
        email_otp.email = user.email
        email_otp.save()
        # return JsonResponse({'status': 'success', 'message': 'User Created'})
        return SuccessResponse()
    else:
        errors = {key: e for key, e in form.errors.items()}
        # return JsonResponse({'status': 'error', 'message': 'Invalid Form', 'errors': errors}, status=400)
        return ErrorResponse(400, CarbureError.INVALID_REGISTRATION_FORM, data=errors)
