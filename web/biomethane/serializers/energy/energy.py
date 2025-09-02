from rest_framework import serializers

from biomethane.models.biomethane_energy import BiomethaneEnergy


class BaseBiomethaneEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEnergy
        exclude = ["year", "status", "producer"]


class BiomethaneEnergySerializer(BaseBiomethaneEnergySerializer):
    class Meta(BaseBiomethaneEnergySerializer.Meta):
        exclude = []


class BiomethaneEnergyInputSerializer(BaseBiomethaneEnergySerializer):
    def validate(self, data):
        errors = {}
        validated_data = super().validate(data)

        validated_data["status"] = BiomethaneEnergy.PENDING

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        if BiomethaneEnergy.objects.filter(producer=entity, year=year).exists():
            raise serializers.ValidationError({"producer": ["Une production d'énergie existe déjà pour cette entité."]})

        validated_data["producer"] = entity
        validated_data["year"] = year

        return super().create(validated_data)
