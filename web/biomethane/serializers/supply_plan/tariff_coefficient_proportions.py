from rest_framework import serializers

from biomethane.services.supply_plan.primary_crop_proportion import compute_primary_crop_proportion
from biomethane.services.supply_plan.tariff_coefficient import compute_tariff_coefficient_proportions


class TariffCoefficientsSerializer(serializers.Serializer):
    """P1 / P2 / P3 / P / Pef shares from the tariff decree referential."""

    p1 = serializers.FloatField(read_only=True)
    p2 = serializers.FloatField(read_only=True)
    p3 = serializers.FloatField(read_only=True)
    p = serializers.FloatField(read_only=True)
    pef = serializers.FloatField(read_only=True)


class TariffCoefficientProportionsSerializer(serializers.Serializer):
    tariff_coefficients = TariffCoefficientsSerializer(read_only=True)
    primary_crop = serializers.FloatField(read_only=True)

    def to_representation(self, queryset):
        return {
            "tariff_coefficients": compute_tariff_coefficient_proportions(queryset),
            "primary_crop": compute_primary_crop_proportion(queryset),
        }
