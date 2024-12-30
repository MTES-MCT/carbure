from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserResendActivationLinkSerializer(serializers.Serializer):
    """
    A serializer for re-sending the user activation email. Includes email field only.
    """

    email = serializers.EmailField(label=_("Email"))

    default_error_messages = {
        "unknown_user": _("Utilisateur inconnu."),
    }

    def validate_email(self, value):
        user_email = value.lower()

        # Vérifie si l'utilisateur existe en base de données
        if not get_user_model().objects.filter(email__iexact=user_email).exists():
            raise serializers.ValidationError(self.default_error_messages["unknown_user"], code="invalid")

        return user_email
