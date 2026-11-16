from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

AUTHORIZATION_FIELDS = ("type", "status", "holder", "parent")
AUTHORIZATION_ERROR = _("Opération non autorisée.")


def validate_authorization(attrs, context):
    """Refuse a type and status the handler does not allow for this actor."""
    parent = attrs.get("parent")
    handler = context["handler"]

    if parent is not None and parent.industry != handler.industry:
        raise serializers.ValidationError(AUTHORIZATION_ERROR)

    if not handler.can_create_action(attrs["type"], attrs["status"], parent):
        raise serializers.ValidationError(AUTHORIZATION_ERROR)

    if not handler.can_assign_status(context["entity"], attrs["type"], attrs["status"], attrs["holder"], parent):
        raise serializers.ValidationError(AUTHORIZATION_ERROR)
