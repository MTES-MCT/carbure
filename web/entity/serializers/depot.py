from rest_framework import serializers
from core.models import Depot, Pays, Entity


class DepotSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(write_only=True)
    entity_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Depot
        fields = "__all__"

    def create(self, validated_data):
        country_code = validated_data.pop("country_code")
        country = Pays.objects.get(code_pays=country_code)
        validated_data["country"] = country

        entity_id = validated_data.pop("entity_id")
        entity = Entity.objects.get(id=entity_id)
        validated_data["entity"] = entity

        validated_data["is_enabled"] = False

        return super().create(validated_data)
