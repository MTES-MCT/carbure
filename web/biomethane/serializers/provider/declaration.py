from django.db.models import Manager
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from biomethane.models import BiomethaneAnnualDeclaration, BiomethaneContract
from biomethane.serializers.production_unit.production_unit import BiomethaneProductionUnitPreviewSerializer
from biomethane.serializers.supply_plan.tariff_coefficient_proportions import TariffCoefficientsSerializer
from biomethane.services.provider_declaration import get_declaration_energy_metrics, get_declaration_energy_values
from biomethane.services.supply_plan.tariff_coefficient import (
    compute_tariff_coefficient_summaries_for_declarations,
    get_tariff_coefficient_summary,
)
from core.models.entity import Entity


class ProviderTariffCoefficientsSerializer(TariffCoefficientsSerializer):
    non_primed = serializers.FloatField(read_only=True)


class EntityPreviewSerializer(serializers.ModelSerializer):
    unique_identification_number = serializers.CharField(
        source="biomethane_injection_site.unique_identification_number",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Entity
        fields = ["unique_identification_number", "name", "entity_type", "registration_id"]


class TariffTonnagesSerializer(ProviderTariffCoefficientsSerializer):
    """Wet matter tonnages (tMB) by tariff coefficient, including unclassified inputs in the total."""

    total = serializers.FloatField(read_only=True)


class BiomethaneProviderDeclarationListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        declarations = list(data.all() if isinstance(data, Manager) else data)
        self.context["tariff_coefficient_summaries"] = compute_tariff_coefficient_summaries_for_declarations(declarations)
        self.context["declaration_energies"] = get_declaration_energy_values(declarations)
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
    electricity_consumption = serializers.SerializerMethodField(help_text="Electricity consumption in kWe.")
    energy_efficiency_coefficient = serializers.SerializerMethodField(
        help_text="Energy efficiency coefficient according to the tariff reference."
    )

    class Meta:
        list_serializer_class = BiomethaneProviderDeclarationListSerializer

    @extend_schema_field(ProviderTariffCoefficientsSerializer(allow_null=True))
    def get_tariff_coefficients(self, obj):
        summary = self._get_tariff_summary(obj)
        if summary is None:
            return None
        tonnages = summary["tonnages"]
        non_primed = self._non_primed_tonnage(tonnages)
        proportion = round(non_primed / tonnages["total"] * 100, 2) if tonnages["total"] else 0.0
        return {**summary["proportions"], "non_primed": proportion}

    @extend_schema_field(TariffTonnagesSerializer(allow_null=True))
    def get_tariff_tonnages(self, obj):
        summary = self._get_tariff_summary(obj)
        if summary is None:
            return None
        tonnages = summary["tonnages"]
        return {
            **{key: round(value, 2) for key, value in tonnages.items()},
            "non_primed": round(self._non_primed_tonnage(tonnages), 2),
        }

    @extend_schema_field(serializers.FloatField())
    def get_electricity_consumption(self, obj):
        return self._get_energy_metrics(obj)[0]

    @extend_schema_field(serializers.FloatField())
    def get_energy_efficiency_coefficient(self, obj):
        return self._get_energy_metrics(obj)[1]

    def _get_tariff_summary(self, obj):
        if "tariff_coefficient_summaries" not in self.context:
            self.context["tariff_coefficient_summaries"] = compute_tariff_coefficient_summaries_for_declarations([obj])
        return get_tariff_coefficient_summary(obj, self.context["tariff_coefficient_summaries"])

    @staticmethod
    def _non_primed_tonnage(tonnages):
        return max(0.0, tonnages["total"] - sum(value for key, value in tonnages.items() if key != "total"))

    def _get_energy_metrics(self, obj):
        if "declaration_energies" not in self.context:
            self.context["declaration_energies"] = get_declaration_energy_values([obj])
        return get_declaration_energy_metrics(obj, self.context["declaration_energies"])
