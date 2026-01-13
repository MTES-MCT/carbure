from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services import BiomethaneAnnualDeclarationService


class BiomethaneAnnualDeclarationSerializer(serializers.ModelSerializer):
    missing_fields = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    status = serializers.ChoiceField(
        choices=[
            (BiomethaneAnnualDeclaration.IN_PROGRESS, BiomethaneAnnualDeclaration.IN_PROGRESS),
            (BiomethaneAnnualDeclaration.DECLARED, BiomethaneAnnualDeclaration.DECLARED),
            (BiomethaneAnnualDeclaration.OVERDUE, BiomethaneAnnualDeclaration.OVERDUE),
        ],
        required=False,
    )

    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["producer", "year", "status", "missing_fields", "is_complete", "is_open"]
        read_only_fields = ["missing_fields", "is_complete", "is_open"]

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
                "supply_plan_valid": {
                    "type": "boolean",
                    "nullable": False,
                    "description": "Whether the supply plan is valid",
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

    def update(self, instance, validated_data):
        if not instance.is_open:
            raise serializers.ValidationError(
                {"status": "La déclaration annuelle n'est pas modifiable dans son état actuel."}
            )

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
