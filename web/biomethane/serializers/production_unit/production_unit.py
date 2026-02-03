from rest_framework import serializers

from biomethane.models import BiomethaneProductionUnit
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Department


class BaseBiomethaneProductionUnitSerializer(serializers.ModelSerializer):
    installed_meters = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneProductionUnit.INSTALLED_METERS_CHOICES),
        required=False,
    )
    digestate_valorization_methods = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneProductionUnit.DIGESTATE_VALORIZATION_METHODS_CHOICES),
        required=False,
    )
    spreading_management_methods = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneProductionUnit.SPREADING_MANAGEMENT_METHODS_CHOICES),
        required=False,
    )
    department = serializers.SlugRelatedField(
        slug_field="code_dept",
        queryset=Department.objects.all(),
        required=False,
    )

    class Meta:
        model = BiomethaneProductionUnit
        exclude = ["created_by"]


class BiomethaneProductionUnitSerializer(BaseBiomethaneProductionUnitSerializer):
    class Meta(BaseBiomethaneProductionUnitSerializer.Meta):
        exclude = []


class BiomethaneProductionUnitUpsertSerializer(BaseBiomethaneProductionUnitSerializer):
    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["created_by"] = entity
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Check if annual declaration needs to be reset
        if BiomethaneAnnualDeclarationService.has_watched_field_changed(instance, validated_data.keys()):
            BiomethaneAnnualDeclarationService.reset_annual_declaration_status(instance.producer)
        return super().update(instance, validated_data)
