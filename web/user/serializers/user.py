from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from core.serializers import UserRightsRequestsSerializer, UserRightsSerializer

User = get_user_model()


class UserErrors:
    EMAIL_ALREADY_USED = "EMAIL_ALREADY_USED"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    INVALID_DATA = "INVALID_DATA"
    EMAIL_UPDATE_SUCCESS = "EMAIL_UPDATE_SUCCESS"


class UserSettingsResponseSeriaizer(serializers.Serializer):
    email = serializers.EmailField()
    rights = UserRightsSerializer(many=True)
    requests = UserRightsRequestsSerializer(many=True)


class UpdateEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_new_email(self, value):
        normalized_email = User.objects.normalize_email(value)
        if User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError(UserErrors.EMAIL_ALREADY_USED)
        return normalized_email

    def validate_password(self, value):
        user = self.context["request"].user
        if not authenticate(username=user.email, password=value):
            raise serializers.ValidationError(UserErrors.INVALID_PASSWORD)
        return value


class ResponseSuccessSerializer(serializers.Serializer):
    status = serializers.CharField()
