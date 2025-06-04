from django.utils.translation import gettext as _
from rest_framework import serializers


class UserResendActivationLinkSerializer(serializers.Serializer):
    """
    A serializer for re-sending the user activation email. Includes email field only.
    """

    email = serializers.EmailField(label=_("Email"))

    def validate_email(self, value):
        user_email = value.lower()
        return user_email
