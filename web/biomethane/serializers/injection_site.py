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

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")

        if request and hasattr(request, "data"):
            data = request.data

            if data.get("is_different_from_production_site") == "false":
                address_fields = ["company_address", "city", "postal_code"]
                for field_name in address_fields:
                    if field_name in fields:
                        fields[field_name].required = False

        return fields

    def validate(self, data):
        if data.get("is_shared_injection_site") and not data.get("unique_identification_number"):
            raise serializers.ValidationError({"unique_identification_number": ["Ce champ est obligatoire."]})
        if data.get("is_different_from_production_site"):
            required_fields = ["company_address", "city", "postal_code"]
            errors = {["Ce champ est obligatoire."] for field in required_fields if not data.get(field)}
            if errors:
                raise serializers.ValidationError(errors)
        return super().validate(data)

    def create(self, validated_data):
        entity = self.context.get("entity")
        if entity:
            if BiomethaneInjectionSite.objects.filter(entity=entity).exists():
                raise serializers.ValidationError({"entity": ["Un site d'injection existe déjà pour cette entité."]})
            validated_data["entity"] = entity

        return super().create(validated_data)
