from rest_framework import serializers

from biomethane.services.supply_plan.tariff_coefficient import compute_tariff_coefficient_proportions


class TariffCoefficientProportionsSerializer(serializers.Serializer):
    p1 = serializers.FloatField(read_only=True)
    p2 = serializers.FloatField(read_only=True)
    p3 = serializers.FloatField(read_only=True)
    p = serializers.FloatField(read_only=True)
    peff = serializers.FloatField(read_only=True)

    def to_representation(self, queryset):
        return compute_tariff_coefficient_proportions(queryset)
