from rest_framework import serializers
from core.models import Depot, Pays, Entity


class DepotSerializer(serializers.ModelSerializer):
    country_code = serializers.SlugRelatedField(slug_field="code_pays", queryset=Pays.objects.all(), write_only=True)
    entity_id = serializers.SlugRelatedField(slug_field="id", queryset=Entity.objects.all(), write_only=True)

    class Meta:
        model = Depot
        fields = "__all__"

    def validate(self, data):
        if data.get("depot_type") == Depot.COGENERATION_PLANT:
            if (
                data.get("thermal_efficiency") is None
                or data.get("electrical_efficiency") is None
                or data.get("useful_temperature") is None
            ):
                raise serializers.ValidationError(
                    "Les paramètres thermal_efficiency, electrical_efficiency et useful_temperature sont obligatoires"
                )

        elif data.get("depot_type") == Depot.HEAT_PLANT:
            if data.get("thermal_efficiency") is None:
                raise serializers.ValidationError("Le paramètre thermal_efficiency est obligatoire")

        elif data.get("depot_type") == Depot.POWER_PLANT:
            if data.get("electrical_efficiency") is None:
                raise serializers.ValidationError("Le paramètre electrical_efficiency est obligatoire")

        return data

    def create(self, validated_data):
        validated_data["country"] = validated_data.pop("country_code")
        validated_data["entity"] = validated_data.pop("entity_id")
        validated_data["is_enabled"] = False

        depot_instance = Depot(**validated_data)
        depot_instance.full_clean()
        depot_instance.save()
        return depot_instance
