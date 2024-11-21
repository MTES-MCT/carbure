from rest_framework import serializers

from core.models import Entity


class EntityResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["entity_type", "name", "id"]
