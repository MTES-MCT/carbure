from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.models.biomethane_contract import BiomethaneContract
from core.serializers import EntityPreviewSerializer


class BiomethaneAdminAnnualDeclarationSerializer(serializers.Serializer):
    """Serializer pour la liste admin des déclarations annuelles biométhane (DREAL)."""

    status = serializers.ChoiceField(
        choices=BiomethaneAnnualDeclaration.ADMIN_DASHBOARD_STATUS_CHOICES,
        source="_computed_status",
        read_only=True,
    )
    producer = EntityPreviewSerializer(read_only=True, source="*")
    tariff_reference = serializers.ChoiceField(
        choices=BiomethaneContract.TARIFF_REFERENCE_CHOICES,
        source="biomethane_contract.tariff_reference",
        read_only=True,
        allow_null=True,
    )
    effective_date = serializers.DateField(
        source="biomethane_contract.effective_date",
        read_only=True,
        allow_null=True,
    )
    department = serializers.CharField(source="_department_code", read_only=True, allow_null=True)
    year = serializers.IntegerField(read_only=True)
