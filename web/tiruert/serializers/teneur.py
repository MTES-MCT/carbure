from rest_framework import serializers

from tiruert.models import Operation


class SimulationInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            "customs_category",
            "biofuel",
            "debited_entity",
            "target_volume",
            "target_emission",
        ]
        extra_kwargs = {
            "biofuel": {"required": True},
            "customs_category": {"required": True},
            "debited_entity": {"required": True},
            "target_volume": {"required": True},
            "target_emission": {"required": True},
        }

    target_volume = serializers.FloatField()
    target_emission = serializers.FloatField()


class SimulationOutputSerializer(serializers.Serializer):
    lot_id = serializers.IntegerField()
    volume = serializers.DecimalField(max_digits=20, decimal_places=2)
    saved_ghg = serializers.DecimalField(max_digits=20, decimal_places=2)
