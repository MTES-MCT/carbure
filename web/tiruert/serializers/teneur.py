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
