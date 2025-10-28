from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneProductionUnit
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService


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

    class Meta:
        model = BiomethaneProductionUnit
        exclude = ["producer"]


class BiomethaneProductionUnitSerializer(BaseBiomethaneProductionUnitSerializer):
    class Meta(BaseBiomethaneProductionUnitSerializer.Meta):
        exclude = []


class BiomethaneProductionUnitUpsertSerializer(BaseBiomethaneProductionUnitSerializer):
    def validate(self, data):
        errors = {}
        validated_data = super().validate(data)

        if "has_sanitary_approval" in validated_data:
            if validated_data["has_sanitary_approval"] and not validated_data.get("sanitary_approval_number"):
                errors["sanitary_approval_number"] = _("Ce champ est obligatoire lorsque l'agrément sanitaire est activé.")

        if "has_hygienization_exemption" in validated_data:
            if validated_data.get("has_hygienization_exemption") and not validated_data.get("hygienization_exemption_type"):
                errors["hygienization_exemption_type"] = _(
                    "Ce champ est obligatoire lorsque la dérogation à l'hygiénisation est activée."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["producer"] = entity
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Check if annual declaration needs to be reset
        if BiomethaneAnnualDeclarationService.has_watched_field_changed(instance, validated_data.keys()):
            BiomethaneAnnualDeclarationService.reset_annual_declaration_status(instance.producer)
        return super().update(instance, validated_data)
