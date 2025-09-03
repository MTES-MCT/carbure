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
        entity = self.context.get("entity")

        validated_data["producer"] = entity

        errors = {}

        if validated_data.get("is_shared_injection_site") and not validated_data.get("meter_number"):
            errors["meter_number"] = [_("Ce champ est obligatoire.")]
        elif not validated_data.get("is_shared_injection_site"):
            validated_data["meter_number"] = None

        if validated_data.get("is_different_from_production_site"):
            required_fields = ["company_address", "city", "postal_code"]
            for field in required_fields:
                if not validated_data.get(field):
                    errors[field] = [_("Ce champ est obligatoire.")]
        else:
            validated_data["company_address"] = None
            validated_data["city"] = None
            validated_data["postal_code"] = None

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data
