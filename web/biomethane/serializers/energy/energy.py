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
        injected_biomethane_gwh_pcs_per_year = attrs.get("injected_biomethane_gwh_pcs_per_year") if attrs.get("injected_biomethane_gwh_pcs_per_year") is not None else att_instance.get("injected_biomethane_gwh_pcs_per_year")
        pcs_kwh_per_nm3 = attrs.get("injected_biomethane_pcs_kwh_per_nm3") if attrs.get("injected_biomethane_pcs_kwh_per_nm3") is not None else att_instance.get("injected_biomethane_pcs_kwh_per_nm3")
        produced_biogas_nm3_per_year = attrs.get("produced_biogas_nm3_per_year") if attrs.get("produced_biogas_nm3_per_year") is not None else att_instance.get("produced_biogas_nm3_per_year")

        if (injected_biomethane_gwh_pcs_per_year is not None and
            pcs_kwh_per_nm3 is not None and
            produced_biogas_nm3_per_year is not None):

            injected_biomethane_nm3_per_year = (injected_biomethane_gwh_pcs_per_year * 10**6) / pcs_kwh_per_nm3
            if (injected_biomethane_nm3_per_year - produced_biogas_nm3_per_year) > 0 :
                raise serializers.ValidationError("The injected biomethane volume does not match the produced biogas volume.")

        

        return attrs


    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        validated_data["producer"] = entity
        validated_data["year"] = year
        print("validated_data", validated_data)
        return super().create(validated_data)
    
