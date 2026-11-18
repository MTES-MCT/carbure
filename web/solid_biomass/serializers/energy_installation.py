from rest_framework import serializers

from solid_biomass.models import EnergyInstallation


class EnergyInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyInstallation
        fields = [
            "production_type",
            "heat_type",
            "commissioning_date",
            "useful_temperature",
            "electrical_efficiency",
            "thermal_efficiency",
            "icpe_number",
            "icpe_regime",
        ]

    def validate(self, attrs):
        production_type = attrs.get("production_type", getattr(self.instance, "production_type", None))
        if production_type not in (EnergyInstallation.HEAT, EnergyInstallation.COGENERATION):
            attrs["heat_type"] = None
        if production_type != EnergyInstallation.COGENERATION:
            attrs["useful_temperature"] = None
        if production_type not in (EnergyInstallation.ELECTRICITY, EnergyInstallation.COGENERATION):
            attrs["electrical_efficiency"] = None
        if production_type not in (EnergyInstallation.HEAT, EnergyInstallation.COGENERATION):
            attrs["thermal_efficiency"] = None
        return attrs
