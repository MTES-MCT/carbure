from rest_framework import serializers

from biomethane.models import BiomethaneDigestate
from biomethane.serializers.digestate.spreading import BiomethaneDigestateSpreadingSerializer
from core.serializers import check_fields_required


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
    def validate(self, data):
        from biomethane.services import BiomethaneDigestateService

        validated_data = super().validate(data)

        # Use the service to get the required fields
        required_fields = BiomethaneDigestateService.get_required_fields(validated_data)

        # Check that all required fields are present and non-empty
        check_fields_required(validated_data, required_fields)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        validated_data["producer"] = entity
        validated_data["year"] = year

        return super().create(validated_data)
