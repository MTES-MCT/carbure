from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password1 = serializers.CharField(label=_("Password"), write_only=True)
    password2 = serializers.CharField(label=_("Password confirmation"), write_only=True)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": _("The two password fields didn't match.")})

        try:
            password_validation.validate_password(data["password2"], self.instance)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password2": e.messages})

        return data
