from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from traceability.models import ActionStatus


class ActionStatusAuthorizationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ActionStatus.STATUSES)

    def validate(self, attrs):
        action = self.instance
        handler = self.context["handler"]

        if not ActionStatus.can_transition(action.status, attrs["status"]):
            raise serializers.ValidationError({"status": _("Changement de statut non autorisé.")})

        if not handler.can_assign_status(self.context["entity"], action.type, attrs["status"], action.holder, action.parent):
            raise serializers.ValidationError(_("Opération non autorisée."))

        return attrs
