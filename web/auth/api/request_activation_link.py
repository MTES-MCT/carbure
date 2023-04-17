from accounts.forms import UserResendActivationLinkForm
from accounts.tokens import account_activation_token
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def request_activation_link(request):
    form = UserResendActivationLinkForm(request.POST)
    if form.is_valid():
        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(email=form.clean_email())
            current_site = get_current_site(request)
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
            # return JsonResponse({'status': 'success'})
            return SuccessResponse()
        except Exception:
            # return JsonResponse({'status': 'error', 'message': 'Could not resend activation link'}, status=400)
            return ErrorResponse(400, CarbureError.ACTIVATION_LINK_ERROR)
    # return JsonResponse({'status': 'error', 'message': 'Invalid Form'}, status=400)
    return ErrorResponse(400, CarbureError.ACTIVATION_LINK_INVALID_FORM)
