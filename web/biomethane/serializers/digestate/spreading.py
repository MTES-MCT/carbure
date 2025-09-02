from rest_framework import serializers

from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading


class BaseBiomethaneDigestateSpreadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneDigestateSpreading
        fields = [
            "spreading_department",
            "spread_quantity",
            "spread_parcels_area",
        ]


class BiomethaneDigestateSpreadingSerializer(BaseBiomethaneDigestateSpreadingSerializer):
    class Meta(BaseBiomethaneDigestateSpreadingSerializer.Meta):
        fields = BaseBiomethaneDigestateSpreadingSerializer.Meta.fields + ["id"]


class BiomethaneDigestateSpreadingAddSerializer(BaseBiomethaneDigestateSpreadingSerializer):
    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        if not year:
            raise serializers.ValidationError({"year": ["Année manquante."]})

        digestate = BiomethaneDigestate.objects.filter(producer=entity, year=year).first()
        if not digestate:
            raise serializers.ValidationError({"year": ["Digestat manquant."]})

        validated_data["digestate"] = digestate

        return super().create(validated_data)
