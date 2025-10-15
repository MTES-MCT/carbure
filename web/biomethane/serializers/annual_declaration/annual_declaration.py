from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services import BiomethaneAnnualDeclarationService
from biomethane.utils import get_declaration_period


class BiomethaneAnnualDeclarationSerializer(serializers.ModelSerializer):
    missing_fields = serializers.SerializerMethodField()
    is_ready = serializers.SerializerMethodField()

    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["year", "status", "missing_fields", "is_ready"]
        read_only_fields = ["year", "missing_fields", "is_ready"]

    def get_missing_fields(self, instance):
        if not hasattr(self, "_missing_fields_cache"):
            self._missing_fields_cache = BiomethaneAnnualDeclarationService.get_missing_fields(instance)
        return self._missing_fields_cache

    def get_is_ready(self, instance):
        missing_fields = self.get_missing_fields(instance)
        return (
            len(missing_fields.get("digestate_missing_fields", [])) == 0
            and len(missing_fields.get("energy_missing_fields", [])) == 0
        )

    def create(self, validated_data):
        validated_data["producer"] = self.context["entity"]
        validated_data["year"] = get_declaration_period()
        return super().create(validated_data)
