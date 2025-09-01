from rest_framework import serializers

from biomethane.models.biomethane_energy import BiomethaneEnergy


class BaseBiomethaneEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEnergy
        fields = [
            "id",
            "injected_biomethane_gwh_pcs_per_year",
            "injected_biomethane_nm3_per_year",
            "injected_biomethane_ch4_rate_percent",
            "injected_biomethane_pcs_kwh_per_nm3",
            "operating_hours",
            "produced_biogas_nm3_per_year",
            "flared_biogas_nm3_per_year",
            "flared_biogas_nm3_per_year",
            "flaring_operating_hours",
            "attest_no_fossil_for_digester_heating_and_purification",
            "energy_used_for_digester_heating",
            "fossil_details_for_digester_heating",
            "attest_no_fossil_for_installation_needs",
            "energy_used_for_installation_needs",
            "fossil_details_for_installation_needs",
            "purified_biogas_quantity_nm3",
            "purification_electric_consumption_kwe",
            "self_consumed_biogas_nm3",
            "total_unit_electric_consumption_kwe",
            "butane_or_propane_addition",
            "fossil_fuel_consumed_kwh",
            "has_opposition_or_complaints_acceptability",
            "estimated_work_days_acceptability",
        ]


class BiomethaneEnergySerializer(BaseBiomethaneEnergySerializer):
    class Meta(BaseBiomethaneEnergySerializer.Meta):
        fields = BaseBiomethaneEnergySerializer.Meta.fields + ["year", "status"]


class BiomethaneEnergyPatchSerializer(BaseBiomethaneEnergySerializer):
    def update(self, instance, validated_data):
        validated_data["status"] = BiomethaneEnergy.PENDING
        return super().update(instance, validated_data)


class BiomethaneEnergyAddSerializer(BaseBiomethaneEnergySerializer):
    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        if not entity:
            raise serializers.ValidationError({"entity": ["Entité manquante."]})

        if BiomethaneEnergy.objects.filter(producer=entity, year=year).exists():
            raise serializers.ValidationError({"producer": ["Une production d'énergie existe déjà pour cette entité."]})

        validated_data["producer"] = entity
        validated_data["year"] = year

        return super().create(validated_data)
