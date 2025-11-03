from rest_framework import serializers

from biomethane.models import BiomethaneInjectionSite
from core.serializers import check_fields_required


class BiomethaneInjectionSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneInjectionSite
        fields = "__all__"


class BiomethaneInjectionSiteInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneInjectionSite
        exclude = ["producer"]
        extra_kwargs = {
            "network_type": {"required": True},
            "network_manager_name": {"required": True},
        }

    def validate(self, data):
        validated_data = super().validate(data)

        required_fields = []

        if validated_data.get("is_shared_injection_site"):
            required_fields.append("meter_number")

        if validated_data.get("is_different_from_production_site"):
            required_fields.extend(["company_address", "city", "postal_code"])

        check_fields_required(validated_data, required_fields)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["producer"] = entity
        return super().create(validated_data)
