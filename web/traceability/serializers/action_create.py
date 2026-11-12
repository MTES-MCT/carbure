from rest_framework import serializers

from core.models import Entity
from traceability.models import Action, ActionStatus


class ActionCreateSerializer(serializers.ModelSerializer):
    """Common request fields; authorization is validated separately before creation."""

    parent = serializers.PrimaryKeyRelatedField(queryset=Action.objects.all(), required=False, allow_null=True)
    type = serializers.ChoiceField(choices=Action.TYPES)
    status = serializers.ChoiceField(choices=ActionStatus.STATUSES, write_only=True)
    holder = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())

    class Meta:
        model = Action
        fields = ["type", "parent", "status", "holder"]

    def create(self, validated_data):
        # The endpoint records the initial status after saving the action.
        validated_data.pop("status", None)
        return super().create(validated_data)
