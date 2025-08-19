from rest_framework import serializers

from biomethane.models import BiomethaneProductionUnit
from core.serializers import NullableMixin


class BaseBiomethaneProductionUnitSerializer(NullableMixin, serializers.ModelSerializer):
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

    def _validate_conditional_fields(self, data):
        errors = {}

        # Conditional validation: sanitary_approval_number required when has_sanitary_approval is True
        if data.get("has_sanitary_approval") and not data.get("sanitary_approval_number"):
            errors["sanitary_approval_number"] = "Ce champ est obligatoire lorsque l'agrément sanitaire est activé."

        # Conditional validation: hygienization_exemption_type required when has_hygienization_exemption is True
        if data.get("has_hygienization_exemption") and not data.get("hygienization_exemption_type"):
            errors["hygienization_exemption_type"] = (
                "Ce champ est obligatoire lorsque la dérogation à l'hygiénisation est activée."
            )

        if errors:
            raise serializers.ValidationError(errors)


class BiomethaneProductionUnitSerializer(BaseBiomethaneProductionUnitSerializer):
    installed_meters = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneProductionUnit.INSTALLED_METERS_CHOICES), read_only=True
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


class BiomethaneProductionUnitAddSerializer(BaseBiomethaneProductionUnitSerializer):
    def validate(self, data):
        self._validate_conditional_fields(data)
        return data

    def create(self, validated_data):
        entity = self.context.get("entity")
        if entity:
            if BiomethaneProductionUnit.objects.filter(producer=entity).exists():
                raise serializers.ValidationError({"producer": ["Une unité de production existe déjà pour cette entité."]})
            validated_data["producer"] = entity
        else:
            raise serializers.ValidationError({"producer": ["Entité manquante."]})

        return super().create(validated_data)


class BiomethaneProductionUnitPatchSerializer(BaseBiomethaneProductionUnitSerializer):
    def validate(self, data):
        # For partial updates, we need to merge with existing instance data
        if self.instance:
            # Get current instance data
            current_data = {}
            for field in self.fields:
                if hasattr(self.instance, field):
                    current_data[field] = getattr(self.instance, field)

            # Merge with new data
            merged_data = {**current_data, **data}
        else:
            merged_data = data

        self._validate_conditional_fields(merged_data)
        return data
