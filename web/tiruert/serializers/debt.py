from rest_framework import serializers

from core.models import MatierePremiere
from tiruert.serializers.balance import BalanceBiofuelSerializer
from tiruert.serializers.fields import TruncatedFloatField
from tiruert.serializers.teneur import SimulationLotOutputSerializer, SimulationMinMaxInputSerializer


class DebtSummarySerializer(serializers.Serializer):
    biofuel = BalanceBiofuelSerializer()
    customs_category = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)
    remaining_volume = TruncatedFloatField()
    remaining_tco2 = serializers.FloatField(min_value=0)


class DebtRepaymentSimulationInputSerializer(SimulationMinMaxInputSerializer):
    class Meta(SimulationMinMaxInputSerializer.Meta):
        fields = [
            "customs_category",
            "biofuel",
            "debited_entity",
            "unit",
            "ges_bound_min",
            "ges_bound_max",
            "feedstock",
            "origin_country",
            "durability_period",
        ]
        extra_kwargs = {
            "customs_category": {"required": True},
            "biofuel": {"required": True, "allow_null": False},
            "debited_entity": {"required": True, "allow_null": False},
        }

    target_volume = None


class DebtRepaymentSimulationSerializer(serializers.Serializer):
    selected_lots = SimulationLotOutputSerializer(many=True)
    total_volume = serializers.FloatField()
    repaid_tco2 = serializers.FloatField(help_text="Cumulative tCO2 credited to the debt at 0.01 t precision.")
    remaining_tco2 = serializers.FloatField(min_value=0)
    debt_tco2 = serializers.FloatField(min_value=0)
