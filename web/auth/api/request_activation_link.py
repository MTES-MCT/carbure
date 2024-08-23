from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

from auth.tokens import account_activation_token
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse


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


class UserResendActivationLinkForm(forms.Form):
    """
    A form for re-sending the user activation email. Includes email field only
    """

    error_messages = {
        "unknown_user": _("Utilisateur inconnu."),
    }

    email = forms.CharField(label=_("Email"), widget=forms.EmailInput)

    def clean_email(self):
        user_email = self.cleaned_data["email"]
        user_email = user_email.lower()

        field_lookup = {"email__iexact": user_email}
        if not get_user_model().objects.filter(**field_lookup).exists():
            raise ValidationError(self.error_messages["unknown_user"], code="invalid")
        return user_email
