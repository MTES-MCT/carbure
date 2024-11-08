from django.core.validators import RegexValidator
from rest_framework import serializers


class VerifyOTPSerializer(serializers.Serializer):
    """
    A serializer for submitting the OTP sent via email. Includes otp_token field only.
    """

    otp_token = serializers.CharField(
        max_length=6,
        min_length=6,
        validators=[RegexValidator(r"^\d{6}$")],
        label="Entrez le code à 6 chiffres reçu par email",
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_otp_token(self, value):
        # Place for any additional validation on otp_token if needed
        return value
