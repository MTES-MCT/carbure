from django import forms
from django.contrib.auth.decorators import login_required
from django.core.validators import RegexValidator
from django.utils import timezone
from django_otp import login as login_with_device
from django_otp import user_has_device
from django_otp.plugins.otp_email.models import EmailDevice

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse


@login_required
def verify_otp(request):
    # for old users that did not register when 2fa was introduced
    if not user_has_device(request.user):
        email_otp = EmailDevice()
        email_otp.user = request.user
        email_otp.name = "email"
        email_otp.confirmed = True
        email_otp.email = request.user.email
        email_otp.save()

    form = OTPForm(request.user, request.POST)
    if form.is_valid():
        device = EmailDevice.objects.get(user=request.user)
        if device.verify_token(form.clean_otp_token()):
            login_with_device(request, device)
            # return JsonResponse({'status': 'success'})
            return SuccessResponse()
        else:
            is_allowed, _ = device.verify_is_allowed()
            now = timezone.now()
            if now > device.valid_until:
                # return JsonResponse({'status': 'error', 'message': 'Code expired'}, status=400)
                return ErrorResponse(400, CarbureError.OTP_EXPIRED_CODE)
            elif device.token != form.clean_otp_token():
                # return JsonResponse({'status': 'error', 'message': 'Code invalid'}, status=400)
                return ErrorResponse(400, CarbureError.OTP_INVALID_CODE)
            elif not is_allowed:
                # return JsonResponse({'status': 'error', 'message': 'Rate limited'}, status=400)
                return ErrorResponse(400, CarbureError.OTP_RATE_LIMITED)
            else:
                # return JsonResponse({'status': 'error', 'message': 'Unknown error'}, status=400)
                return ErrorResponse(400, CarbureError.OTP_UNKNOWN_ERROR)
    # return JsonResponse({'status': 'error', 'message': 'Invalid Form'}, status=400)
    return ErrorResponse(400, CarbureError.OTP_INVALID_FORM)


class OTPForm(forms.Form):
    """
    A form for submitting the OTP sent via email. Includes otp_token field only
    """

    otp_token = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[RegexValidator(r"^\d{6}$")],
        label="Entrez le code à 6 chiffres reçu par email",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    def __init__(self, user, *args, **kwargs):
        super(OTPForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_otp_token(self):
        otp_token = self.cleaned_data["otp_token"]
        return otp_token
