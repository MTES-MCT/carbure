from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.serializers.annual_declaration.annual_declaration import (
    BiomethaneAnnualDeclarationStatusSerializer,
)
from core.serializers import EntityPreviewSerializer


class BiomethaneAdminAnnualDeclarationSerializer(BiomethaneAnnualDeclarationStatusSerializer):
    """Serializer pour la liste admin des déclarations annuelles biométhane (DREAL)."""

    producer = EntityPreviewSerializer()
    tariff_reference = serializers.CharField(
        source="producer.biomethane_contract.tariff_reference",
        read_only=True,
        allow_null=True,
    )
    effective_date = serializers.DateField(
        source="producer.biomethane_contract.effective_date",
        read_only=True,
        allow_null=True,
    )
    department = serializers.CharField(
        source="producer.biomethane_production_unit.department.code_dept",
        read_only=True,
        allow_null=True,
    )

    class Meta(BiomethaneAnnualDeclarationStatusSerializer.Meta):
        model = BiomethaneAnnualDeclaration
        fields = BiomethaneAnnualDeclarationStatusSerializer.Meta.fields + [
            "id",
            "producer",
            "effective_date",
            "tariff_reference",
            "department",
            "year",
        ]
