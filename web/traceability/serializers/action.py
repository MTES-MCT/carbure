from rest_framework import serializers

from traceability.models.action import Action


class ActionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Action
        fields = "__all__"


class ActionInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        exclude = ["id"]
