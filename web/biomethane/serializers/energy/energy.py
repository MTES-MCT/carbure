from rest_framework import serializers

from biomethane.models.biomethane_energy import BiomethaneEnergy


class BaseBiomethaneEnergySerializer(serializers.ModelSerializer):
    malfunction_types = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneEnergy.MALFUNCTION_TYPES),
        required=False,
    )

    class Meta:
        model = BiomethaneEnergy
        exclude = ["producer", "year"]


class BiomethaneEnergySerializer(BaseBiomethaneEnergySerializer):
    class Meta(BaseBiomethaneEnergySerializer.Meta):
        exclude = []


class BiomethaneEnergyInputSerializer(BaseBiomethaneEnergySerializer):
    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        validated_data["producer"] = entity
        validated_data["year"] = year
        return super().create(validated_data)
