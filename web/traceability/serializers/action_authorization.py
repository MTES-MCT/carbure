from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import Entity
from traceability.models import Action, ActionStatus


class ActionAuthorizationSerializer(serializers.Serializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Action.objects.all(), required=False, allow_null=True)
    type = serializers.ChoiceField(choices=Action.TYPES)
    status = serializers.ChoiceField(choices=ActionStatus.STATUSES)
    holder = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())

    def validate(self, attrs):
        parent = attrs.get("parent")
        handler = self.context["handler"]

        if parent is not None and parent.industry != handler.industry:
            raise serializers.ValidationError(_("Opération non autorisée."))

        if not handler.can_create_action(attrs["type"], attrs["status"], parent):
            raise serializers.ValidationError(_("Opération non autorisée."))

        if not handler.can_assign_status(self.context["entity"], attrs["type"], attrs["status"], attrs["holder"], parent):
            raise serializers.ValidationError(_("Opération non autorisée."))

        return attrs
