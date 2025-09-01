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
        exclude = ["entity"]

    def validate(self, data):
        errors = {}

        entity = self.context.get("entity")
        if entity:
            data["entity"] = entity
        else:
            errors["entity"] = [_("Entité manquante.")]

        if data.get("is_shared_injection_site") and not data.get("meter_number"):
            errors["meter_number"] = [_("Ce champ est obligatoire.")]
        elif not data.get("is_shared_injection_site"):
            data["meter_number"] = None

        if data.get("is_different_from_production_site"):
            required_fields = ["company_address", "city", "postal_code"]
            for field in required_fields:
                if not data.get(field):
                    errors[field] = [_("Ce champ est obligatoire.")]
        elif not data.get("is_different_from_production_site"):
            data["company_address"] = None
            data["city"] = None
            data["postal_code"] = None

        if errors:
            raise serializers.ValidationError(errors)

        return super().validate(data)
