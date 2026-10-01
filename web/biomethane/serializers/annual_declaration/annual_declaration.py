from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services import BiomethaneAnnualDeclarationService
from biomethane.services.annual_declaration.notification import reopen_declaration


class BiomethaneAnnualDeclarationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["status"]

    status = serializers.ChoiceField(
        choices=BiomethaneAnnualDeclaration.DECLARATION_STATUS_CHOICES,
        required=False,
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["status"] = getattr(instance, "computed_status", None)
        return representation


class BiomethaneAnnualDeclarationSerializer(BiomethaneAnnualDeclarationStatusSerializer):
    missing_fields = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()

    class Meta(BiomethaneAnnualDeclarationStatusSerializer.Meta):
        model = BiomethaneAnnualDeclaration
        fields = BiomethaneAnnualDeclarationStatusSerializer.Meta.fields + [
            "producer",
            "year",
            "missing_fields",
            "is_complete",
            "is_open",
            "submission_date",
        ]
        read_only_fields = ["missing_fields", "is_complete", "submission_date"]

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
                "contract_missing_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "nullable": True,
                    "description": "List of missing fields for contract",
                },
                "production_unit_missing_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "nullable": True,
                    "description": "List of missing fields for production unit",
                },
                "injection_missing_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "nullable": True,
                    "description": "List of missing fields for injection",
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
        """
        Producer correction: an open declaration can only be set back to IN_PROGRESS.
        DECLARED is set by the validate action. A closed declaration cannot be edited.
        """
        if not instance.is_open:
            raise serializers.ValidationError(
                {"status": "La déclaration annuelle n'est pas modifiable dans son état actuel."}
            )

        validated_data = {key: value for key, value in validated_data.items() if key == "status"}

        status = validated_data.get("status")
        if status is not None:
            if (
                instance.status == BiomethaneAnnualDeclaration.IN_PROGRESS
                and status == BiomethaneAnnualDeclaration.IN_PROGRESS
            ):
                validated_data.pop("status")
            elif status != BiomethaneAnnualDeclaration.IN_PROGRESS:
                raise serializers.ValidationError(
                    {"status": f"Seul le statut {BiomethaneAnnualDeclaration.IN_PROGRESS} est autorisé."}
                )

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if validated_data:
            instance.save()

        return instance


class BiomethaneAnnualDeclarationDrealSerializer(BiomethaneAnnualDeclarationSerializer):
    def update(self, instance, validated_data):
        if "is_open" not in validated_data:
            return instance

        is_open = validated_data["is_open"]
        if is_open and not instance.is_open:
            reopen_declaration(instance, request=self.context.get("request"))
            return instance

        if instance.is_open != is_open:
            instance.is_open = is_open
            instance.save(update_fields=["is_open"])

        return instance
