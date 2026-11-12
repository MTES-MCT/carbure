from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import Entity
from traceability.models import Action, ActionStatus


class ActionAuthorizationSerializer(serializers.Serializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Action.objects.all(), required=False, allow_null=True)
    type = serializers.ChoiceField(choices=Action.TYPES)
    status = serializers.ChoiceField(choices=ActionStatus.STATUSES)
    holder = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())

    @staticmethod
    def find_edge(handler, action_type, status, parent=None):
        parent_state = (parent.type, parent.status) if parent is not None else None
        for edge in handler.action_creation_flow:
            source, target, _authorize = edge
            if source == parent_state and target == (action_type, status):
                return edge
        return None

    def validate(self, attrs):
        parent = attrs.get("parent")
        holder = attrs["holder"]
        handler = self.context["handler"]
        actor = self.context["entity"]

        if parent is not None and parent.industry != handler.industry:
            raise serializers.ValidationError(_("Opération non autorisée."))

        edge = self.find_edge(handler, attrs["type"], attrs["status"], parent)
        if edge is None:
            raise serializers.ValidationError(_("Opération non autorisée."))

        authorize = edge[2]
        parent_holder = parent.holder if parent is not None else None
        if authorize is None or not authorize(actor, parent_holder, holder):
            raise serializers.ValidationError(_("Opération non autorisée."))

        return attrs
