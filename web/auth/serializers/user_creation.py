from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from auth.serializers.credentials import validate_password_confirmation, validated_name

User = get_user_model()


class UserCreationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users. Includes required fields
    and repeated password validation.
    """

    password1 = serializers.CharField(label=_("Password"), write_only=True)
    password2 = serializers.CharField(label=_("Password confirmation"), write_only=True)

    class Meta:
        model = User
        fields = (User.USERNAME_FIELD,) + tuple(User.REQUIRED_FIELDS) + ("password1", "password2")
        extra_kwargs = {
            "email": {"validators": []},  # Disable default validators for email, to avoid enumeration of existing accounts
            "name": {"required": True, "allow_blank": False},
        }

    def validate_email(self, value):
        """
        Validate and normalize the email address, without raising an exception if it already exists.
        """
        return User.objects.normalize_email(value)

    def validate_name(self, value):
        return validated_name(value)

    def validate(self, data):
        # The account does not exist yet. Similarity is checked against the submitted name and email.
        user = User(**{k: v for k, v in data.items() if k not in ("password1", "password2")})
        validate_password_confirmation(data["password1"], data["password2"], user)
        return data

    def create(self, validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2")

        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()
        return user
