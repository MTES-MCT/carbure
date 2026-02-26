from rest_framework import serializers

from biomethane.models import BiomethaneSupplyPlan
from biomethane.serializers.supply_plan.supply_input import BiomethaneSupplyInputSerializer
from core.utils import check_file_size_and_extension


class BiomethaneSupplyPlanSerializer(serializers.ModelSerializer):
    inputs = BiomethaneSupplyInputSerializer(many=True, read_only=True, source="supply_inputs")

    class Meta:
        model = BiomethaneSupplyPlan
        exclude = ["id"]


class BiomethaneUploadExcelSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        return check_file_size_and_extension(value, max_size_mb=10, extensions=[".xlsx", ".xls"])
