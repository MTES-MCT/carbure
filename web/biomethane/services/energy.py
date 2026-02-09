from dataclasses import dataclass
from typing import Optional

from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.services.rules import FieldClearingRule, RuleBuilder, get_fields_from_applied_rules


@dataclass
class EnergyContext:
    """Context data extracted from an energy instance."""

    instance: object  # The energy instance
    production_unit: Optional[object] = None
    contract: Optional[object] = None

    @property
    def has_malfunctions(self) -> bool:
        return getattr(self.instance, "has_malfunctions", False)

    @property
    def malfunction_types(self) -> Optional[list]:
        return getattr(self.instance, "malfunction_types", None) or []

    @property
    def has_injection_difficulties(self) -> bool:
        return getattr(self.instance, "has_injection_difficulties_due_to_network_saturation", False)

    @property
    def energy_types(self) -> Optional[list]:
        return getattr(self.instance, "energy_types", None) or []

    @property
    def tariff_reference(self) -> Optional[str]:
        return getattr(self.contract, "tariff_reference", None) if self.contract else None

    @property
    def installation_category(self) -> Optional[str]:
        return getattr(self.contract, "installation_category", None) if self.contract else None


class BiomethaneEnergyService:
    """
    Centralized service to manage energy business logic.
    All validation rules and conditional field logic are defined here.
    """

    # Fields for tariff reference 2011, 2020, 2021
    OLD_TARIFF_FIELDS = [
        "purified_biogas_quantity_nm3",
        "purification_electric_consumption_kwe",
    ]

    # Fields for tariff reference 2023
    NEW_TARIFF_FIELDS = [
        "self_consumed_biogas_nm3",
        "total_unit_electric_consumption_kwe",
    ]

    MALFUNCTION_FIELDS = [
        "malfunction_cumulative_duration_days",
        "malfunction_types",
        "malfunction_details",
    ]

    MALFUNCTION_DETAILS_FIELD = ["malfunction_details"]

    INJECTION_DIFFICULTY_FIELDS = ["injection_impossibility_hours"]

    # Fields conditional on energy types (PRODUCED_BIOGAS or PRODUCED_BIOMETHANE)
    ENERGY_TYPE_CONDITIONAL_FIELDS = [
        "self_consumed_biogas_or_biomethane_kwh",
    ]

    ENERGY_DETAILS_FIELD = ["energy_details"]

    # Fields not included in the rules, but they are related to other models for calculation purposes
    EXTRA_OPTIONAL_FIELDS = ["energy_types"]

    @staticmethod
    def _extract_data(instance) -> EnergyContext:
        """Extract data from an energy instance and return structured context."""
        from django.core.exceptions import ObjectDoesNotExist

        # Extract producer and related objects
        producer = getattr(instance, "producer", None)
        production_unit = None
        contract = None

        if producer:
            try:
                production_unit = producer.biomethane_production_unit
            except ObjectDoesNotExist:
                production_unit = None

            try:
                contract = producer.biomethane_contract
            except ObjectDoesNotExist:
                contract = None

        # Return structured context
        return EnergyContext(
            instance=instance,
            production_unit=production_unit,
            contract=contract,
        )

    @staticmethod
    def _get_fields_to_clear(instance):
        """
        Return the list of fields to clear for an energy instance.

        Returns:
            list: Fields to clear/empty (also represents optional fields)
        """
        # Extract context
        context = BiomethaneEnergyService._extract_data(instance)

        # Get all configured rules
        rules = _build_energy_rules()

        # Evaluate each rule and collect fields to clear
        return get_fields_from_applied_rules(rules, context)

    @staticmethod
    def get_optional_fields(instance):
        """
        Return the list of optional fields for a given instance.
        Used by the optional_fields property of the model.
        """
        return BiomethaneEnergyService._get_fields_to_clear(instance)

    @staticmethod
    def get_all_optional_fields():
        """
        Return the list of all optional fields for energy instance.
        """
        rules = _build_energy_rules()
        fields = [field for rule in rules for field in rule.fields]

        return fields + BiomethaneEnergyService.EXTRA_OPTIONAL_FIELDS

    @staticmethod
    def get_fields_to_clear(instance):
        """
        Return the list of fields to clear for a given instance.
        Used by signals.
        """
        return BiomethaneEnergyService._get_fields_to_clear(instance)


# Rule configuration: declarative definition of all field clearing rules
def _build_energy_rules() -> list[FieldClearingRule]:
    """
    Build the list of field clearing rules for energy instances.
    """

    return [
        # Tariff rules - Old tariff fields (2011, 2020, 2021)
        RuleBuilder.value_not_in_list(
            lambda ctx: ctx.tariff_reference,
            ["2011", "2020", "2021"],
            BiomethaneEnergyService.OLD_TARIFF_FIELDS,
            "not_old_tariff",
        ),
        # Tariff rules - New tariff fields (2023)
        RuleBuilder.value_not_in_list(
            lambda ctx: ctx.tariff_reference,
            ["2023"],
            BiomethaneEnergyService.NEW_TARIFF_FIELDS,
            "not_new_tariff",
        ),
        # Malfunction rules - no malfunctions
        FieldClearingRule(
            name="no_malfunctions",
            fields=BiomethaneEnergyService.MALFUNCTION_FIELDS,
            condition=lambda ctx: not ctx.has_malfunctions,
        ),
        # Malfunction rules - malfunction type not "OTHER"
        FieldClearingRule(
            name="malfunction_no_other_type",
            fields=BiomethaneEnergyService.MALFUNCTION_DETAILS_FIELD,
            condition=lambda ctx: (
                ctx.has_malfunctions and BiomethaneEnergy.MALFUNCTION_TYPE_OTHER not in ctx.malfunction_types
            ),
        ),
        # Injection difficulty rules
        FieldClearingRule(
            name="no_injection_difficulties",
            fields=BiomethaneEnergyService.INJECTION_DIFFICULTY_FIELDS,
            condition=lambda ctx: not ctx.has_injection_difficulties,
        ),
        # Energy details rules
        FieldClearingRule(
            name="no_fossil_for_energy",
            fields=BiomethaneEnergyService.ENERGY_DETAILS_FIELD,
            condition=lambda ctx: not any(
                energy_type
                in [
                    BiomethaneEnergy.ENERGY_TYPE_FOSSIL,
                    BiomethaneEnergy.ENERGY_TYPE_OTHER_RENEWABLE,
                    BiomethaneEnergy.ENERGY_TYPE_OTHER,
                ]
                for energy_type in ctx.energy_types
            ),
        ),
        # Energy type conditional fields - only visible if PRODUCED_BIOGAS or PRODUCED_BIOMETHANE
        FieldClearingRule(
            name="no_biogas_or_biomethane_energy_type",
            fields=BiomethaneEnergyService.ENERGY_TYPE_CONDITIONAL_FIELDS,
            condition=lambda ctx: not any(
                energy_type
                in [
                    BiomethaneEnergy.ENERGY_TYPE_PRODUCED_BIOGAS,
                    BiomethaneEnergy.ENERGY_TYPE_PRODUCED_BIOMETHANE,
                ]
                for energy_type in ctx.energy_types
            ),
        ),
    ]
