from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services import BiomethaneAnnualDeclarationService


class BiomethaneAnnualDeclarationSerializer(serializers.ModelSerializer):
    missing_fields = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()

    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["year", "status", "missing_fields", "is_complete"]
        read_only_fields = ["year", "missing_fields", "is_complete"]
        writeable_fields = ["status"]
        required_fields = writeable_fields

    def to_representation(self, instance):
        # Override status in representation to use computed value
        representation = super().to_representation(instance)
        representation["status"] = BiomethaneAnnualDeclarationService.get_declaration_status(instance)
        return representation

    @extend_schema_field(
        {
            "type": "object",
            "properties": {
                "digestate_missing_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "nullable": True,
                    "description": "List of missing fields for digestate",
                },
                "energy_missing_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "nullable": True,
                    "description": "List of missing fields for energy",
                },
            },
            "description": "Missing fields grouped by type",
        }
    )
    def get_missing_fields(self, instance):
        if not hasattr(self, "_missing_fields_cache"):
            self._missing_fields_cache = BiomethaneAnnualDeclarationService.get_missing_fields(instance)
        return self._missing_fields_cache

    @extend_schema_field({"type": "boolean"})
    def get_is_complete(self, instance):
        missing_fields = self.get_missing_fields(instance)
        return BiomethaneAnnualDeclarationService.is_declaration_complete(instance, missing_fields)

    def create(self, validated_data):
        validated_data["producer"] = self.context["entity"]
        validated_data["year"] = BiomethaneAnnualDeclarationService.get_declaration_period()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Allow partial update of the declaration, only for status field to IN_PROGRESS
        status = validated_data.get("status")
        if status is not None:
            if instance.status == BiomethaneAnnualDeclaration.IN_PROGRESS:
                return instance

            if status == BiomethaneAnnualDeclaration.IN_PROGRESS:
                instance.status = status
                instance.save()
            else:
                raise serializers.ValidationError(
                    {"status": f"Seul le statut {BiomethaneAnnualDeclaration.IN_PROGRESS} est autorisé."}
                )
        return instance
