from django.utils.translation import gettext as _
from rest_framework import serializers


class UserResendActivationLinkSerializer(serializers.Serializer):
    """Resend the activation email from an email address, or from the account id carried by an expired link."""

    email = serializers.EmailField(label=_("Email"), required=False, allow_blank=True)
    uidb64 = serializers.CharField(required=False, allow_blank=True)
    token = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        return value.lower()
