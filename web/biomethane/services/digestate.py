from dataclasses import dataclass
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist

from biomethane.models import BiomethaneDigestate, BiomethaneProductionUnit
from biomethane.services.rules import FieldClearingRule, RuleBuilder, get_fields_from_applied_rules


@dataclass
class DigestateContext:
    """Context data extracted from a digestate instance."""

    instance: object  # The digestate instance
    production_unit: Optional[object] = None
    contract: Optional[object] = None

    @property
    def composting_locations(self) -> list:
        locations = getattr(self.instance, "composting_locations", [])
        return locations if locations else []


class BiomethaneDigestateService:
    """
    Centralized service to manage digestate business logic.
    All validation rules and conditional field logic are defined here.
    """

    # Field groups definition (class constants)
    EXTERNAL_PLATFORM_FIELDS = [
        "external_platform_name",
        "external_platform_digestate_volume",
        "external_platform_department",
        "external_platform_municipality",
    ]
    ON_SITE_FIELDS = ["on_site_composted_digestate_volume"]
    RAW_DIGESTATE_FIELDS = ["raw_digestate_tonnage_produced", "raw_digestate_dry_matter_rate"]
    SEPARATED_DIGESTATE_FIELDS = ["solid_digestate_tonnage", "liquid_digestate_quantity"]
    SPREADING_FIELDS = ["average_spreading_valorization_distance"]
    INCINERATION_FIELDS = ["annual_eliminated_volume", "incinerator_landfill_center_name"]
    WWTP_FIELDS = ["wwtp_materials_to_incineration"]
    SALE_FIELDS = ["sold_volume", "acquiring_companies"]

    @staticmethod
    def _extract_data(instance) -> DigestateContext:
        """Extract data from a digestate instance and return structured context."""
        # Extract producer and related objects
        producer = getattr(instance, "producer", None)
        production_unit = None
        contract = None

        if producer:
            try:
                production_unit = BiomethaneProductionUnit.objects.filter(created_by=producer).first()
            except ObjectDoesNotExist:
                production_unit = None

            try:
                contract = producer.biomethane_contract
            except ObjectDoesNotExist:
                contract = None

        # Return structured context
        return DigestateContext(
            instance=instance,
            production_unit=production_unit,
            contract=contract,
        )

    @staticmethod
    def _get_fields_to_clear(instance):
        """
        Return the list of fields to clear for a digestate instance.

        Returns:
            list: Fields to clear/empty (also represents optional fields)
        """
        # Extract context
        context = BiomethaneDigestateService._extract_data(instance)

        # Get all configured rules
        rules = _build_digestate_rules()

        # Evaluate each rule and collect fields to clear
        return get_fields_from_applied_rules(rules, context)

    @staticmethod
    def get_optional_fields(instance):
        """
        Return the list of optional fields for a given instance.
        Used by the optional_fields property of the model.
        """
        return BiomethaneDigestateService._get_fields_to_clear(instance)

    @staticmethod
    def get_fields_to_clear(instance):
        """
        Return the list of fields to clear for a given instance.
        Used by signals.
        """
        return BiomethaneDigestateService._get_fields_to_clear(instance)


# Rule configuration: declarative definition of all field clearing rules
def _build_digestate_rules() -> list[FieldClearingRule]:
    """
    Build the list of field clearing rules for digestate instances.
    """
    from biomethane.models import BiomethaneContract, BiomethaneProductionUnit

    return [
        # Phase separation rules
        FieldClearingRule(
            name="phase_separation_enabled",
            fields=BiomethaneDigestateService.RAW_DIGESTATE_FIELDS,
            condition=lambda ctx: (ctx.production_unit and ctx.production_unit.has_digestate_phase_separation),
        ),
        FieldClearingRule(
            name="phase_separation_disabled",
            fields=BiomethaneDigestateService.SEPARATED_DIGESTATE_FIELDS,
            condition=lambda ctx: (ctx.production_unit and not ctx.production_unit.has_digestate_phase_separation),
        ),
        # Valorization method rules
        RuleBuilder.required_value_not_in_list(
            lambda ctx: ctx.production_unit.digestate_valorization_methods if ctx.production_unit else [],
            BiomethaneProductionUnit.SPREADING,
            BiomethaneDigestateService.SPREADING_FIELDS,
            "spreading_not_selected",
        ),
        RuleBuilder.required_value_not_in_list(
            lambda ctx: ctx.production_unit.digestate_valorization_methods if ctx.production_unit else [],
            BiomethaneProductionUnit.INCINERATION_LANDFILLING,
            BiomethaneDigestateService.INCINERATION_FIELDS + BiomethaneDigestateService.WWTP_FIELDS,
            "incineration_not_selected",
        ),
        # Composting rules
        # Parent rule: composting disabled → clear all composting fields
        RuleBuilder.required_value_not_in_list(
            lambda ctx: ctx.production_unit.digestate_valorization_methods if ctx.production_unit else [],
            BiomethaneProductionUnit.COMPOSTING,
            BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS
            + BiomethaneDigestateService.ON_SITE_FIELDS
            + ["composting_locations"],
            "composting_disabled",
        ),
        # Child rule 1: external platform not selected
        FieldClearingRule(
            name="external_platform_not_selected",
            fields=BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS,
            condition=lambda ctx: (
                ctx.production_unit
                and BiomethaneProductionUnit.COMPOSTING in (ctx.production_unit.digestate_valorization_methods or [])
                and BiomethaneDigestate.EXTERNAL_PLATFORM not in ctx.composting_locations
            ),
        ),
        # Child rule 2: on-site not selected
        FieldClearingRule(
            name="on_site_not_selected",
            fields=BiomethaneDigestateService.ON_SITE_FIELDS,
            condition=lambda ctx: (
                ctx.production_unit
                and BiomethaneProductionUnit.COMPOSTING in (ctx.production_unit.digestate_valorization_methods or [])
                and BiomethaneDigestate.ON_SITE not in ctx.composting_locations
            ),
        ),
        # Spreading management rules
        RuleBuilder.required_value_not_in_list(
            lambda ctx: ctx.production_unit.spreading_management_methods if ctx.production_unit else [],
            BiomethaneProductionUnit.SALE,
            BiomethaneDigestateService.SALE_FIELDS,
            "sale_not_selected",
        ),
        # Contract rules
        RuleBuilder.contract_category_not(
            BiomethaneContract.INSTALLATION_CATEGORY_2,
            BiomethaneDigestateService.WWTP_FIELDS,
            "wwtp_category_not_2",
        ),
    ]
