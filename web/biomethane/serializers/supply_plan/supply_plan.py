import os

from rest_framework import serializers

from biomethane.models import BiomethaneSupplyPlan
from biomethane.serializers.supply_plan.supply_input import BiomethaneSupplyInputSerializer


class BiomethaneSupplyPlanSerializer(serializers.ModelSerializer):
    inputs = BiomethaneSupplyInputSerializer(many=True, read_only=True, source="supply_inputs")

    class Meta:
        model = BiomethaneSupplyPlan
        exclude = ["id"]


class BiomethaneUploadExcelSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        # Check extension
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in [".xlsx"]:
            raise serializers.ValidationError("Le fichier doit avoir une extension .xlsx")

        # Check MIME type if available
        allowed_types = [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        ]

        if hasattr(value, "content_type") and value.content_type:
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Le type de fichier n'est pas supporté. Utilisez un fichier Excel.")

        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Le fichier est trop volumineux (maximum 10MB)")

        return value
