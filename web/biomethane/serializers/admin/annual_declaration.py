from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.serializers.annual_declaration.annual_declaration import (
    BiomethaneAnnualDeclarationStatusSerializer,
)


class BiomethaneAdminAnnualDeclarationSerializer(BiomethaneAnnualDeclarationStatusSerializer):
    """Serializer pour la liste admin des déclarations annuelles biométhane (DREAL)."""

    entity_name = serializers.CharField(source="producer.name", read_only=True)
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
    department = serializers.SerializerMethodField()

    class Meta(BiomethaneAnnualDeclarationStatusSerializer.Meta):
        model = BiomethaneAnnualDeclaration
        fields = BiomethaneAnnualDeclarationStatusSerializer.Meta.fields + [
            "id",
            "entity_name",
            "effective_date",
            "tariff_reference",
            "department",
            "year",
        ]

    @extend_schema_field(
        {
            "type": "string",
        }
    )
    def get_department(self, declaration):
        production_unit = getattr(declaration.producer, "biomethane_production_unit", None)
        if production_unit and production_unit.department:
            return production_unit.department.code_dept

        zipcode = getattr(declaration.producer, "registered_zipcode", None)

        return zipcode or None
