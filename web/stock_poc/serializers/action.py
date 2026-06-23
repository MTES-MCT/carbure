from decimal import Decimal

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from stock_poc.models import Action


class ActionSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    available = serializers.SerializerMethodField()

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

    @extend_schema_field(serializers.DecimalField(max_digits=20, decimal_places=2))
    def get_available(self, obj) -> Decimal:
        # Use the annotation when present, otherwise compute it from children.
        annotated = getattr(obj, "available", None)
        if annotated is not None:
            return annotated
        children = obj.children.exclude(status=Action.REFUSED)
        used = sum((child.quantity for child in children), Decimal("0"))
        return obj.quantity - used


class ActionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ["id", "type", "status", "quantity", "parent", "owner"]
        extra_kwargs = {"owner": {"required": False}}

    def create(self, validated_data):
        # Owner is optional: default to the current entity when not provided.
        validated_data.setdefault("owner", self.context["entity"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "owner" not in validated_data:
            validated_data["owner"] = instance.owner
        return super().update(instance, validated_data)
