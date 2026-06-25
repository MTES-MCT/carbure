from rest_framework import serializers

from stock_poc.models import Action
from stock_poc.models.action_status import ActionStatus


class ActionSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    available = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Action
        fields = [
            "id",
            "type",
            "status",
            "quantity",
            "available",
            "owner",
            "owner_name",
            "parent",
            "created_at",
        ]


class ActionCreateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=ActionStatus.STATUSES)

    class Meta:
        model = Action
        fields = ["id", "type", "quantity", "parent", "owner", "status"]
        extra_kwargs = {"owner": {"required": False}}

    def create(self, validated_data):
        status = validated_data.pop("status")
        # Owner is optional: default to the current entity when not provided.
        validated_data.setdefault("owner", self.context["entity"])

        action = Action.objects.create(**validated_data)
        ActionStatus.objects.create(action=action, status=status)

        return action

    def update(self, instance, validated_data):
        if "owner" not in validated_data:
            validated_data["owner"] = instance.owner

        status = validated_data.pop("status")
        ActionStatus.objects.create(action=instance, status=status)

        return super().update(instance, validated_data)
