from rest_framework import serializers

from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.serializers.energy.monthly_report import BiomethaneEnergyMonthlyReportSerializer


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

    class Meta(BaseBiomethaneEnergySerializer.Meta):
        exclude = []


class BiomethaneEnergyInputSerializer(BaseBiomethaneEnergySerializer):
    def validate(self, attrs):
        att_instance = self.instance.__dict__.copy() if self.instance else {}
        key_1 = "injected_biomethane_gwh_pcs_per_year"
        key_2 = "injected_biomethane_pcs_kwh_per_nm3"
        key_3 = "produced_biogas_nm3_per_year"
        key_4 = "injected_biomethane_ch4_rate_percent"
        key_5 = "flared_biogas_nm3_per_year"
        key_6 = "self_consumed_biogas_nm3"

        injected_biomethane_gwh_pcs_per_year = attrs.get(key_1, att_instance.get(key_1))
        pcs_kwh_per_nm3 = attrs.get(key_2, att_instance.get(key_2))
        produced_biogas_nm3_per_year = attrs.get(key_3, att_instance.get(key_3))
        injected_biomethane_ch4_rate_percent = attrs.get(key_4, att_instance.get(key_4))
        flared_biogas_nm3_per_year = attrs.get(key_5, att_instance.get(key_5))
        self_consumed_biogas_nm3 = attrs.get(key_6, att_instance.get(key_6))

        if None not in (
            injected_biomethane_gwh_pcs_per_year,
            pcs_kwh_per_nm3,
            produced_biogas_nm3_per_year,
            injected_biomethane_ch4_rate_percent,
            flared_biogas_nm3_per_year,
            self_consumed_biogas_nm3,
        ):
            biogas_ch4_rate_percent = 55
            acceptation_threshold = 0.25
            injected_methane_nm3_per_year = (
                (injected_biomethane_gwh_pcs_per_year * 10**6)
                * injected_biomethane_ch4_rate_percent
                / (pcs_kwh_per_nm3 * 100)
            )
            expected_methane_nm3_per_year = (
                (produced_biogas_nm3_per_year - flared_biogas_nm3_per_year - self_consumed_biogas_nm3)
                * biogas_ch4_rate_percent
                / 100
            )

            if (
                abs(injected_methane_nm3_per_year - expected_methane_nm3_per_year)
                > acceptation_threshold * expected_methane_nm3_per_year
            ):
                raise serializers.ValidationError(
                    {
                        "biomethane_volume_error": [
                            "Le volume de méthane injecté ne correspond pas à la part de méthane de la production de biogaz."
                        ]
                    }
                )

        return attrs

    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        validated_data["producer"] = entity
        validated_data["year"] = year
        return super().create(validated_data)
