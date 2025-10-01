from rest_framework import serializers

from biomethane.models import BiomethaneSupplyPlan
from biomethane.serializers.supply_plan.supply_input import BiomethaneSupplyInputSerializer


class BiomethaneSupplyPlanSerializer(serializers.ModelSerializer):
    inputs = BiomethaneSupplyInputSerializer(many=True, read_only=True, source="supply_inputs")

    class Meta:
        model = BiomethaneSupplyPlan
        exclude = ["id"]
