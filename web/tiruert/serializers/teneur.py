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
            "max_n_batches",
            "enforced_volumes",
        ]
        extra_kwargs = {
            "biofuel": {"required": True},
            "customs_category": {"required": True},
            "debited_entity": {"required": True},
        }

    target_volume = serializers.FloatField(required=True)
    target_emission = serializers.FloatField(required=True)
    max_n_batches = serializers.IntegerField(required=False)
    enforced_volumes = serializers.ListField(child=serializers.IntegerField(), required=False)


class SimulationLotOutputSerializer(serializers.Serializer):
    lot_id = serializers.IntegerField()
    volume = serializers.FloatField()
    emission_rate_per_mj = serializers.FloatField()


class SimulationOutputSerializer(serializers.Serializer):
    selected_lots = SimulationLotOutputSerializer(many=True)
    fun = serializers.FloatField()


class SimulationMinMaxInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            "customs_category",
            "biofuel",
            "debited_entity",
            "target_volume",
        ]
        extra_kwargs = {
            "biofuel": {"required": True},
            "customs_category": {"required": True},
            "debited_entity": {"required": True},
            "target_volume": {"required": True},
        }

    target_volume = serializers.FloatField()


class SimulationMinMaxOutputSerializer(serializers.Serializer):
    min_avoided_emissions = serializers.FloatField()
    max_avoided_emissions = serializers.FloatField()
