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
        if data.get("is_shared_injection_site") and not data.get("unique_identification_number"):
            raise serializers.ValidationError({"unique_identification_number": ["Ce champ est obligatoire."]})
        return super().validate(data)

    def create(self, validated_data):
        entity = self.context.get("entity")
        if entity:
            if BiomethaneInjectionSite.objects.filter(entity=entity).exists():
                raise serializers.ValidationError({"entity": ["Un site d'injection existe déjà pour cette entité."]})
            validated_data["entity"] = entity

        return super().create(validated_data)
