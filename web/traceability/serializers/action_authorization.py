from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import Entity
from traceability.models import Action


class ActionAuthorizationSerializer(serializers.Serializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Action.objects.all(), required=False, allow_null=True)
    type = serializers.ChoiceField(choices=Action.TYPES)
    holder = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())

    @staticmethod
    def find_edge(handler, action_type, parent=None):
        parent_state = (parent.type, parent.status) if parent is not None else None
        for edge in handler.action_creation_flow:
            source, (child_type, _status), _authorize = edge
            if source == parent_state and child_type == action_type:
                return edge
        return None

    def validate(self, attrs):
        parent = attrs.get("parent")
        holder = attrs["holder"]
        handler = self.context["handler"]
        actor = self.context["entity"]

        if parent is not None and parent.industry != handler.industry:
            raise serializers.ValidationError(_("Opération non autorisée."))

        edge = self.find_edge(handler, attrs["type"], parent)
        if edge is None:
            raise serializers.ValidationError(_("Opération non autorisée."))

        initial_status = edge[1][1]
        authorize = edge[2]
        parent_holder = parent.holder if parent is not None else None
        if authorize is None or not authorize(actor, parent_holder, holder):
            raise serializers.ValidationError(_("Opération non autorisée."))

        attrs["initial_status"] = initial_status
        return attrs
