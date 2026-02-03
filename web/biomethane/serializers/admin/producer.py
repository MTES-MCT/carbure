from rest_framework import serializers

from core.models import Entity


class BiomethaneProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["id", "name"]
