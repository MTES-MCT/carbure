from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template import loader
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from core.carburetypes import CarbureError

from core.common import ErrorResponse, SuccessResponse


def request_password_reset(request):
    username = request.POST.get("username", "")
    try:
        user = get_user_model().objects.get(email=username)
    except:
        # return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)
        return ErrorResponse(400, CarbureError.PASSWORD_RESET_USER_NOT_FOUND)

    prtg = PasswordResetTokenGenerator()
    current_site = get_current_site(request)
    # send email
    email_subject = "Carbure - Réinitialisation du mot de passe"
    email_context = {
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": prtg.make_token(user),
    }
    html_message = loader.render_to_string("emails/password_reset_email.html", email_context)
    text_message = loader.render_to_string("emails/password_reset_email.txt", email_context)
    send_mail(
        subject=email_subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
        recipient_list=[user.email],
        fail_silently=False,
    )
    # return JsonResponse({'status': 'success'})
    return SuccessResponse()
