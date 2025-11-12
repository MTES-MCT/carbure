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
    def attest_no_fossil_for_digester_heating_and_purification(self) -> bool:
        return getattr(self.instance, "attest_no_fossil_for_digester_heating_and_purification", False)

    @property
    def attest_no_fossil_for_installation_needs(self) -> bool:
        return getattr(self.instance, "attest_no_fossil_for_installation_needs", False)

    @property
    def tariff_reference(self) -> Optional[str]:
        return getattr(self.contract, "tariff_reference", None) if self.contract else None


class BiomethaneEnergyService:
    """
    Centralized service to manage energy business logic.
    All validation rules and conditional field logic are defined here.
    """

    # Field groups definition
    FLARING_FIELDS = ["flaring_operating_hours"]

    # Fields for tariff reference 2011, 2020, 2021
    OLD_TARIFF_FIELDS = [
        "energy_used_for_digester_heating",
        "fossil_details_for_digester_heating",
        "purified_biogas_quantity_nm3",
        "purification_electric_consumption_kwe",
    ]

    # Fields for tariff reference 2023
    NEW_TARIFF_FIELDS = [
        "energy_used_for_installation_needs",
        "fossil_details_for_installation_needs",
        "self_consumed_biogas_nm3",
        "total_unit_electric_consumption_kwe",
    ]

    TARIFF_2011_2020_FIELDS = ["injected_biomethane_nm3_per_year"]

    MALFUNCTION_FIELDS = [
        "malfunction_cumulative_duration_days",
        "malfunction_types",
        "malfunction_details",
    ]

    MALFUNCTION_DETAILS_FIELD = ["malfunction_details"]

    INJECTION_DIFFICULTY_FIELDS = ["injection_impossibility_hours"]

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
    from biomethane.models import BiomethaneProductionUnit

    return [
        # Flaring rules
        RuleBuilder.required_value_not_in_list(
            lambda ctx: ctx.production_unit.installed_meters if ctx.production_unit else [],
            BiomethaneProductionUnit.FLARING_FLOWMETER,
            BiomethaneEnergyService.FLARING_FIELDS,
            "flaring_not_installed",
        ),
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
        # Tariff rules - 2011 and 2020 specific fields
        RuleBuilder.value_not_in_list(
            lambda ctx: ctx.tariff_reference,
            ["2011", "2020"],
            BiomethaneEnergyService.TARIFF_2011_2020_FIELDS,
            "not_2011_2020_tariff",
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
        # Installation energy needs rules
        FieldClearingRule(
            name="no_fossil_for_digester_heating",
            fields=["fossil_details_for_digester_heating"],
            condition=lambda ctx: ctx.attest_no_fossil_for_digester_heating_and_purification,
        ),
        FieldClearingRule(
            name="no_fossil_for_installation_needs",
            fields=["fossil_details_for_installation_needs"],
            condition=lambda ctx: ctx.attest_no_fossil_for_installation_needs,
        ),
    ]
