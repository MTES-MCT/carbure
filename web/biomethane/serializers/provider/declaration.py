from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.serializers.production_unit.production_unit import BiomethaneProductionUnitPreviewSerializer
from core.serializers import EntityPreviewSerializer


class BiomethaneProviderDeclarationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=BiomethaneAnnualDeclaration.DECLARATION_STATUS_CHOICES,
        source="computed_status",
        read_only=True,
    )
    producer = EntityPreviewSerializer(read_only=True)
    production_unit = BiomethaneProductionUnitPreviewSerializer(read_only=True, allow_null=True)
