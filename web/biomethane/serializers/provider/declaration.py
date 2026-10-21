from rest_framework import serializers

from biomethane.serializers.production_unit.production_unit import BiomethaneProductionUnitPreviewSerializer
from core.serializers import EntityPreviewSerializer


class BiomethaneProviderDeclarationSerializer(serializers.Serializer):
    producer = EntityPreviewSerializer(read_only=True)
    production_unit = BiomethaneProductionUnitPreviewSerializer(read_only=True, allow_null=True)
