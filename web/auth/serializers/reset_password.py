from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from auth.serializers.credentials import validate_password_confirmation


class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password1 = serializers.CharField(label=_("Mot de passe"), write_only=True)
    password2 = serializers.CharField(label=_("Confirmation du mot de passe"), write_only=True)

    def validate(self, data):
        validate_password_confirmation(data["password1"], data["password2"], self.instance)
        return data
