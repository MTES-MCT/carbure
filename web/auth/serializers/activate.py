from rest_framework import serializers

from auth.serializers.credentials import validate_password_confirmation, validated_name


class ActivateAccountSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()


class ActivateProfileSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    name = serializers.CharField(max_length=255)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_name(self, value):
        return validated_name(value)

    def validate(self, data):
        # The similarity validator compares the password with the name being submitted.
        self.instance.name = data["name"]
        validate_password_confirmation(data["password1"], data["password2"], self.instance)
        return data
