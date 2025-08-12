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
