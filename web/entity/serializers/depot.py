from rest_framework import serializers

from core.models import Depot, Entity, Pays


class DepotSerializer(serializers.ModelSerializer):
    country_code = serializers.SlugRelatedField(slug_field="code_pays", queryset=Pays.objects.all(), write_only=True)
    entity_id = serializers.SlugRelatedField(slug_field="id", queryset=Entity.objects.all(), write_only=True)

    class Meta:
        model = Depot
        fields = "__all__"

    def create(self, validated_data):
        validated_data["country"] = validated_data.pop("country_code")
        validated_data["entity"] = validated_data.pop("entity_id")
        validated_data["is_enabled"] = False

        depot_instance = Depot(**validated_data)
        depot_instance.full_clean()
        depot_instance.save()
        return depot_instance
