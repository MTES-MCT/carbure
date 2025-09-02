from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneProductionUnit


class BaseBiomethaneProductionUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneProductionUnit
        fields = [
            "unit_name",
            "siret_number",
            "company_address",
            "unit_type",
            "has_sanitary_approval",
            "sanitary_approval_number",
            "has_hygienization_exemption",
            "hygienization_exemption_type",
            "icpe_number",
            "icpe_regime",
            "process_type",
            "methanization_process",
            "production_efficiency",
            "installed_meters",
            "has_hygienization_unit",
            "has_co2_valorization_process",
            "has_digestate_phase_separation",
            "raw_digestate_treatment_steps",
            "liquid_phase_treatment_steps",
            "solid_phase_treatment_steps",
            "digestate_valorization_methods",
            "spreading_management_methods",
            "digestate_sale_type",
        ]


class BiomethaneProductionUnitSerializer(BaseBiomethaneProductionUnitSerializer):
    installed_meters = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneProductionUnit.INSTALLED_METERS_CHOICES),
        read_only=True,
    )
    digestate_valorization_methods = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneProductionUnit.DIGESTATE_VALORIZATION_METHODS_CHOICES),
        read_only=True,
    )
    spreading_management_methods = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneProductionUnit.SPREADING_MANAGEMENT_METHODS_CHOICES),
        read_only=True,
    )

    class Meta(BaseBiomethaneProductionUnitSerializer.Meta):
        fields = ["id", "producer"] + BaseBiomethaneProductionUnitSerializer.Meta.fields


class BiomethaneProductionUnitUpsertSerializer(BaseBiomethaneProductionUnitSerializer):
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

    def validate(self, data):
        errors = {}

        entity = self.context.get("entity")
        data["producer"] = entity

        if "has_sanitary_approval" in data:
            if not data["has_sanitary_approval"]:
                data["sanitary_approval_number"] = None
            elif not data.get("sanitary_approval_number"):
                errors["sanitary_approval_number"] = _("Ce champ est obligatoire lorsque l'agrément sanitaire est activé.")

        if "has_hygienization_exemption" in data:
            if not data.get("has_hygienization_exemption"):
                data["hygienization_exemption_type"] = None
            elif not data.get("hygienization_exemption_type"):
                errors["hygienization_exemption_type"] = _(
                    "Ce champ est obligatoire lorsque la dérogation à l'hygiénisation est activée."
                )

        if data.get("has_digestate_phase_separation"):
            data["raw_digestate_treatment_steps"] = None
        else:
            data["liquid_phase_treatment_steps"] = None
            data["solid_phase_treatment_steps"] = None

        if errors:
            raise serializers.ValidationError(errors)

        return data
