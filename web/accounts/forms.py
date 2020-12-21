from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django_otp import user_has_device, devices_for_user
from django_otp.plugins.otp_email.models import EmailDevice
from django.utils.translation import gettext as _
from django.core.validators import RegexValidator

class UserResendActivationLinkForm(forms.Form):
    """
    A form for re-sending the user activation email. Includes email field only
    """

    error_messages = {
        'unknown_user': _("Utilisateur inconnu."),
    }

    email = forms.CharField(label=_("Email"), widget=forms.EmailInput)

    def clean_email(self):
        user_email = self.cleaned_data["email"]
        user_email = user_email.lower()

        field_lookup = {f"email__iexact": user_email}
        if not get_user_model().objects.filter(**field_lookup).exists():
            raise ValidationError(self.error_messages['unknown_user'], code='invalid')
        return user_email


class OTPForm(forms.Form):
    """
    A form for submitting the OTP sent via email. Includes otp_token field only
    """

    otp_token = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[RegexValidator(r"^\d{6}$")],
        label=f"Entrez le code à 6 chiffres reçu par email",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    def __init__(self, user, *args, **kwargs):
        super(OTPForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_otp_token(self):
        otp_token = self.cleaned_data["otp_token"]
        return otp_token
