from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from auth.validators import clean_name


def validated_name(value):
    try:
        return clean_name(value)
    except ValidationError as exc:
        raise serializers.ValidationError(exc.messages)


def validate_password_confirmation(password1, password2, user):
    if password1 != password2:
        raise serializers.ValidationError({"password2": _("The two password fields didn't match.")})

    try:
        password_validation.validate_password(password2, user)
    except ValidationError as exc:
        raise serializers.ValidationError({"password2": exc.messages})
