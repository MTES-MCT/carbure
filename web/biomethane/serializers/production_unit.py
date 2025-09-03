from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneProductionUnit


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
        exclude = ["id", "producer"]


class BiomethaneProductionUnitSerializer(BaseBiomethaneProductionUnitSerializer):
    class Meta(BaseBiomethaneProductionUnitSerializer.Meta):
        exclude = []


class BiomethaneProductionUnitUpsertSerializer(BaseBiomethaneProductionUnitSerializer):
    def validate(self, data):
        errors = {}
        validated_data = super().validate(data)

        entity = self.context.get("entity")
        validated_data["producer"] = entity

        if "has_sanitary_approval" in validated_data:
            if not validated_data["has_sanitary_approval"]:
                validated_data["sanitary_approval_number"] = None
            elif not validated_data.get("sanitary_approval_number"):
                errors["sanitary_approval_number"] = _("Ce champ est obligatoire lorsque l'agrément sanitaire est activé.")

        if "has_hygienization_exemption" in validated_data:
            if not validated_data.get("has_hygienization_exemption"):
                validated_data["hygienization_exemption_type"] = None
            elif not validated_data.get("hygienization_exemption_type"):
                errors["hygienization_exemption_type"] = _(
                    "Ce champ est obligatoire lorsque la dérogation à l'hygiénisation est activée."
                )

        if validated_data.get("has_digestate_phase_separation"):
            validated_data["raw_digestate_treatment_steps"] = None
        else:
            validated_data["liquid_phase_treatment_steps"] = None
            validated_data["solid_phase_treatment_steps"] = None

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data
