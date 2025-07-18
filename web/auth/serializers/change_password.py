from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class ChangePasswordErrors:
    INVALID_DATA = "INVALID_DATA"
    WRONG_CURRENT_PASSWORD = "WRONG_CURRENT_PASSWORD"
    PASSWORDS_MATCH = "PASSWORDS_MATCH"
    CONFIRM_PASSWORD_MISMATCH = "CONFIRM_PASSWORD_MISMATCH"


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(ChangePasswordErrors.WRONG_CURRENT_PASSWORD)
        return value

    def validate_new_password(self, value):
        user = self.context["request"].user
        validate_password(value, user)
        return value

    def validate(self, attrs):
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        confirm_new_password = attrs.get("confirm_new_password")

        if current_password == new_password:
            raise serializers.ValidationError({"current_password": ChangePasswordErrors.PASSWORDS_MATCH})

        if new_password != confirm_new_password:
            raise serializers.ValidationError({"confirm_new_password": ChangePasswordErrors.CONFIRM_PASSWORD_MISMATCH})

        return attrs
