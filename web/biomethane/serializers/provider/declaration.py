from django.db.models import Manager
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration, BiomethaneContract
from biomethane.serializers.production_unit.production_unit import BiomethaneProductionUnitPreviewSerializer
from biomethane.serializers.supply_plan.tariff_coefficient_proportions import TariffCoefficientsSerializer
from biomethane.services.supply_plan.tariff_coefficient import (
    compute_tariff_coefficient_summaries_for_declarations,
    get_tariff_coefficient_summary,
)
from core.serializers import EntityPreviewSerializer


class TariffTonnagesSerializer(TariffCoefficientsSerializer):
    """Wet matter tonnages (tMB) by tariff coefficient, including unclassified inputs in the total."""

    total = serializers.FloatField(read_only=True)


class BiomethaneProviderDeclarationListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        declarations = list(data.all() if isinstance(data, Manager) else data)
        self.context["tariff_coefficient_summaries"] = compute_tariff_coefficient_summaries_for_declarations(declarations)
        return super().to_representation(declarations)


class BiomethaneProviderDeclarationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=BiomethaneAnnualDeclaration.DECLARATION_STATUS_CHOICES,
        source="computed_status",
        read_only=True,
    )
    producer = EntityPreviewSerializer(read_only=True)
    production_unit = BiomethaneProductionUnitPreviewSerializer(read_only=True, allow_null=True)
    tariff_reference = serializers.ChoiceField(
        choices=BiomethaneContract.TARIFF_REFERENCE_CHOICES,
        source="producer.biomethane_contract.tariff_reference",
        read_only=True,
        allow_null=True,
    )
    tariff_coefficients = serializers.SerializerMethodField(
        help_text="Percentages of the declaration year's total wet matter tonnage, or null without tariff reference data."
    )
    tariff_tonnages = serializers.SerializerMethodField(
        help_text="Wet matter tonnages used to calculate the percentages, or null without tariff reference data."
    )

    class Meta:
        list_serializer_class = BiomethaneProviderDeclarationListSerializer

    @extend_schema_field(TariffCoefficientsSerializer(allow_null=True))
    def get_tariff_coefficients(self, obj):
        if "tariff_coefficient_summaries" not in self.context:
            self.context["tariff_coefficient_summaries"] = compute_tariff_coefficient_summaries_for_declarations([obj])
        summary = get_tariff_coefficient_summary(obj, self.context["tariff_coefficient_summaries"])
        return summary["proportions"] if summary is not None else None

    @extend_schema_field(TariffTonnagesSerializer(allow_null=True))
    def get_tariff_tonnages(self, obj):
        if "tariff_coefficient_summaries" not in self.context:
            self.context["tariff_coefficient_summaries"] = compute_tariff_coefficient_summaries_for_declarations([obj])
        summary = get_tariff_coefficient_summary(obj, self.context["tariff_coefficient_summaries"])
        return summary["tonnages"] if summary is not None else None
