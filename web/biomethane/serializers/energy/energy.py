from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.serializers.energy.monthly_report import BiomethaneEnergyMonthlyReportSerializer
from biomethane.services.consistency_checks import BiomethaneEnergyConsistencyChecksService


class BaseBiomethaneEnergySerializer(serializers.ModelSerializer):
    energy_types = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneEnergy.ENERGY_TYPES_CHOICES),
        required=False,
    )
    malfunction_types = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneEnergy.MALFUNCTION_TYPES_CHOICES),
        required=False,
    )

    class Meta:
        model = BiomethaneEnergy
        exclude = ["producer", "year"]


class BiomethaneEnergySerializer(BaseBiomethaneEnergySerializer):
    monthly_reports = BiomethaneEnergyMonthlyReportSerializer(many=True, read_only=True)

    consistency_warnings = serializers.SerializerMethodField()

    @extend_schema_field(
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "level": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
            "description": "List of consistency warnings for the energy data",
        }
    )
    def get_consistency_warnings(self, instance):
        return BiomethaneEnergyConsistencyChecksService.get_consistency_warnings(instance)

    class Meta(BaseBiomethaneEnergySerializer.Meta):
        exclude = []


class BiomethaneEnergyInputSerializer(BaseBiomethaneEnergySerializer):
    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        validated_data["producer"] = entity
        validated_data["year"] = year
        return super().create(validated_data)
