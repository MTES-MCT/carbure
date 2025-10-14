from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.utils import get_declaration_period


class BiomethaneAnnualDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["producer", "year", "status"]
        read_only_fields = ["producer", "year"]

    def create(self, validated_data):
        validated_data["producer"] = self.context["entity"]
        validated_data["year"] = get_declaration_period()
        return super().create(validated_data)
