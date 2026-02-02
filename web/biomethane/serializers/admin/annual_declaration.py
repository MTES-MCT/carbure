from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService


class BiomethaneAdminAnnualDeclarationSerializer(serializers.ModelSerializer):
    """Serializer pour la liste admin des déclarations annuelles biométhane (DREAL)."""

    entity_name = serializers.CharField(source="producer.name", read_only=True)
    effective_date = serializers.SerializerMethodField()
    tariff_reference = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = [
            "id",
            "entity_name",
            "effective_date",
            "tariff_reference",
            "department",
            "status",
            "year",
        ]

    def get_effective_date(self, declaration):
        contract = getattr(declaration.producer, "biomethane_contract", None)
        return contract.effective_date if contract else None

    def get_tariff_reference(self, declaration):
        contract = getattr(declaration.producer, "biomethane_contract", None)
        return contract.tariff_reference if contract else None

    def get_department(self, declaration):
        production_unit = getattr(declaration.producer, "biomethane_production_unit", None)
        if production_unit and production_unit.department:
            return production_unit.department.code_dept

        zipcode = getattr(declaration.producer, "registered_zipcode", None)

        return zipcode or None

    def get_status(self, declaration):
        return BiomethaneAnnualDeclarationService.get_declaration_status(declaration)
