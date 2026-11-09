from django.utils.translation import gettext as _
from rest_framework import serializers


class UserResendActivationLinkSerializer(serializers.Serializer):
    """Resend the activation email for the pending account matching this address."""

    email = serializers.EmailField(label=_("Email"))

    def validate_email(self, value):
        return value.lower()
