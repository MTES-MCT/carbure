from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class ChangeEmailErrors:
    INVALID_DATA = "INVALID_DATA"
    EMAIL_ALREADY_USED = "EMAIL_ALREADY_USED"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    NO_CHANGE_REQUEST = "NO_CHANGE_REQUEST"
    OTP_CODE_EXPIRED = "OTP_CODE_EXPIRED"
    INVALID_OTP = "INVALID_OTP"


class RequestEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_new_email(self, value):
        normalized_email = User.objects.normalize_email(value)
        if User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError(ChangeEmailErrors.EMAIL_ALREADY_USED)
        return normalized_email

    def validate_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(ChangeEmailErrors.WRONG_PASSWORD)
        return value


class ConfirmEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)
    otp_token = serializers.CharField(required=True, max_length=6)

    def validate_new_email(self, value):
        return User.objects.normalize_email(value)
