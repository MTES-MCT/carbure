from rest_framework import serializers

from biomethane.models.biomethane_energy import BiomethaneEnergy


class BiomethaneEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEnergy
        fields = "__all__"


class BiomethaneEnergyInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEnergy
        exclude = ["year", "producer"]

    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        validated_data["producer"] = entity
        validated_data["year"] = year
        return super().create(validated_data)
