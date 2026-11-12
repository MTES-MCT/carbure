import uuid

from django.db import transaction
from rest_framework import serializers

from traceability.models import Action, ActionStatus


class ValorizeSerializer(serializers.ModelSerializer):
    type = serializers.HiddenField(default=Action.VALORIZE)
    parent = serializers.PrimaryKeyRelatedField(queryset=Action.objects.all())

    class Meta:
        model = Action
        fields = ["type", "parent"]

    @transaction.atomic
    def create(self, validated_data):
        parent = validated_data["parent"]
        action = super().create(
            {
                "pos_id": str(uuid.uuid4()),
                "type": Action.VALORIZE,
                "parent": parent,
                "holder": parent.holder,
                "industry": parent.industry,
                "quantity": parent.quantity,
                "working_date": parent.working_date,
                "material": None,
            }
        )
        ActionStatus.objects.create(action=parent, status=ActionStatus.ACCEPTED)
        return action
