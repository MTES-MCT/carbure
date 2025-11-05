from rest_framework import serializers

from biomethane.models import BiomethaneDigestate
from biomethane.serializers.digestate.spreading import BiomethaneDigestateSpreadingSerializer


class BaseBiomethaneDigestateSerializer(serializers.ModelSerializer):
    composting_locations = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneDigestate.COMPOSTING_LOCATIONS),
        required=False,
    )

    class Meta:
        model = BiomethaneDigestate
        exclude = ["producer", "year"]


class BiomethaneDigestateSerializer(BaseBiomethaneDigestateSerializer):
    spreadings = BiomethaneDigestateSpreadingSerializer(many=True, read_only=True)

    class Meta(BaseBiomethaneDigestateSerializer.Meta):
        exclude = []


class BiomethaneDigestateInputSerializer(BaseBiomethaneDigestateSerializer):
    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        validated_data["producer"] = entity
        validated_data["year"] = year

        return super().create(validated_data)
