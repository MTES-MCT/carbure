from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneInjectionSite


class BiomethaneInjectionSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneInjectionSite
        fields = "__all__"


class BiomethaneInjectionSiteInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneInjectionSite
        exclude = ["producer"]

    def validate(self, data):
        validated_data = super().validate(data)

        errors = {}

        if validated_data.get("is_shared_injection_site") and not validated_data.get("meter_number"):
            errors["meter_number"] = [_("Ce champ est obligatoire.")]

        if validated_data.get("is_different_from_production_site"):
            required_fields = ["company_address", "city", "postal_code"]
            for field in required_fields:
                if not validated_data.get(field):
                    errors[field] = [_("Ce champ est obligatoire.")]

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["producer"] = entity
        return super().create(validated_data)
