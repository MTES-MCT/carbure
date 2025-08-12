from rest_framework import serializers

from biomethane.models import BiomethaneProductionUnit


class BiomethaneProductionUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneProductionUnit
        fields = [
            "id",
            "producer",
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
            "has_biogas_production_flowmeter",
            "has_purification_flowmeter",
            "has_flaring_flowmeter",
            "has_heating_flowmeter",
            "has_purification_electrical_meter",
            "has_global_electrical_meter",
            "has_hygienization_unit",
            "has_co2_valorization_process",
            "has_digestate_phase_separation",
            "raw_digestate_treatment_steps",
            "liquid_phase_treatment_steps",
            "solid_phase_treatment_steps",
            "digestate_valorization_method",
            "spreading_management",
            "digestate_sale_type",
        ]


class BiomethaneProductionUnitAddSerializer(serializers.ModelSerializer):
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
            "has_biogas_production_flowmeter",
            "has_purification_flowmeter",
            "has_flaring_flowmeter",
            "has_heating_flowmeter",
            "has_purification_electrical_meter",
            "has_global_electrical_meter",
            "has_hygienization_unit",
            "has_co2_valorization_process",
            "has_digestate_phase_separation",
            "raw_digestate_treatment_steps",
            "liquid_phase_treatment_steps",
            "solid_phase_treatment_steps",
            "digestate_valorization_method",
            "spreading_management",
            "digestate_sale_type",
        ]

    def validate(self, data):
        # Conditional validation: sanitary_approval_number required when has_sanitary_approval is True
        if data.get("has_sanitary_approval") and not data.get("sanitary_approval_number"):
            raise serializers.ValidationError(
                {"sanitary_approval_number": "Ce champ est obligatoire lorsque l'agrément sanitaire est activé."}
            )

        # Conditional validation: hygienization_exemption_type required when has_hygienization_exemption is True
        if data.get("has_hygienization_exemption") and not data.get("hygienization_exemption_type"):
            raise serializers.ValidationError(
                {
                    "hygienization_exemption_type": "Ce champ est obligatoire lorsque la dérogation à l'hygiénisation est "
                    "activée."
                }
            )

        return data

    def create(self, validated_data):
        entity = self.context.get("entity")
        if entity:
            if BiomethaneProductionUnit.objects.filter(producer=entity).exists():
                raise serializers.ValidationError({"producer": ["Une unité de production existe déjà pour cette entité."]})
            validated_data["producer"] = entity

        return super().create(validated_data)


class BiomethaneProductionUnitPatchSerializer(serializers.ModelSerializer):
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
            "has_biogas_production_flowmeter",
            "has_purification_flowmeter",
            "has_flaring_flowmeter",
            "has_heating_flowmeter",
            "has_purification_electrical_meter",
            "has_global_electrical_meter",
            "has_hygienization_unit",
            "has_co2_valorization_process",
            "has_digestate_phase_separation",
            "raw_digestate_treatment_steps",
            "liquid_phase_treatment_steps",
            "solid_phase_treatment_steps",
            "digestate_valorization_method",
            "spreading_management",
            "digestate_sale_type",
        ]

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

        # Conditional validation: sanitary_approval_number required when has_sanitary_approval is True
        if merged_data.get("has_sanitary_approval") and not merged_data.get("sanitary_approval_number"):
            raise serializers.ValidationError(
                {"sanitary_approval_number": "Ce champ est obligatoire lorsque l'agrément sanitaire est activé."}
            )

        # Conditional validation: hygienization_exemption_type required when has_hygienization_exemption is True
        if merged_data.get("has_hygienization_exemption") and not merged_data.get("hygienization_exemption_type"):
            raise serializers.ValidationError(
                {
                    "hygienization_exemption_type": "Ce champ est obligatoire lorsque la dérogation à l'hygiénisation est "
                    "activée."
                }
            )

        return data
