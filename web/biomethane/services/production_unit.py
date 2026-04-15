from dataclasses import dataclass
from typing import Optional

from biomethane.models.biomethane_contract import BiomethaneContract
from biomethane.services.rules import FieldClearingRule, OptionalFieldRule, get_fields_from_applied_rules


@dataclass
class ProductionUnitContext:
    """Context data extracted from a production unit instance."""

    instance: object
    contract: Optional[object] = None


class BiomethaneProductionUnitService:
    """
    Centralized service to manage production unit business logic.
    All validation rules and conditional field logic are defined here.
    """

    # Conditional field groups
    SANITARY_APPROVAL_FIELDS = ["sanitary_approval_number"]
    HYGIENIZATION_EXEMPTION_FIELDS = ["hygienization_exemption_type"]
    PHASE_SEPARATION_FIELDS = ["liquid_phase_treatment_steps", "solid_phase_treatment_steps"]
    SPREADING_MANAGEMENT_FIELDS = ["spreading_management_methods", "digestate_sale_types"]
    ICPE_FIELDS = ["icpe_number", "icpe_regime"]
    ISDND_RELATED_FIELDS = [
        "process_type",
        "methanization_process",
        "has_hygienization_unit",
        "has_digestate_phase_separation",
        "raw_digestate_treatment_steps",
        "liquid_phase_treatment_steps",
        "solid_phase_treatment_steps",
        "digestate_valorization_methods",
        "spreading_management_methods",
        "digestate_sale_types",
    ]

    # Fields that are never required for the annual declaration completeness check.
    # Includes:
    # - Technical fields inherited from Site (managed during profile creation, not declaration-specific)
    # - Production unit fields that are always optional
    # Note: BooleanField with default values (has_sanitary_approval, etc.) are never None
    # so they are naturally never flagged as missing by _get_missing_fields.
    ALWAYS_OPTIONAL_FIELDS = [
        # Inherited Site fields
        "country",
        "gps_coordinates",
        # Phase separation fields: optional regardless of has_digestate_phase_separation value.
        # They are cleared (set to None) when phase separation is disabled, but never strictly required.
        *PHASE_SEPARATION_FIELDS,
        # Digestate valorization fields: optional regardless of has_digestate_phase_separation value.
        # Cleared (set to None) when phase separation is enabled, but never strictly required.
        "raw_digestate_treatment_steps",
        "installed_meters",
    ]

    @staticmethod
    def _extract_data(instance) -> ProductionUnitContext:
        """Extract data from a production unit instance and return structured context."""
        from django.core.exceptions import ObjectDoesNotExist

        contract = None
        producer = getattr(instance, "producer", None)
        if producer:
            try:
                contract = producer.biomethane_contract
            except ObjectDoesNotExist:
                contract = None

        return ProductionUnitContext(instance=instance, contract=contract)

    @staticmethod
    def get_optional_fields(instance):
        """
        Return the list of optional fields for a given instance.
        Used by the optional_fields property of the model.
        """
        ctx = BiomethaneProductionUnitService._extract_data(instance)
        optional_fields_rules = _build_production_unit_optional_rules()
        clearing_rueles = _build_production_unit_clearing_rules()
        rules = optional_fields_rules + clearing_rueles
        conditional_optional = get_fields_from_applied_rules(rules, ctx)
        return conditional_optional + BiomethaneProductionUnitService.ALWAYS_OPTIONAL_FIELDS

    @staticmethod
    def get_fields_to_clear(instance):
        """
        Return the list of fields to clear for a given instance.
        Used by signals.
        """
        ctx = BiomethaneProductionUnitService._extract_data(instance)
        rules = _build_production_unit_clearing_rules()
        return get_fields_from_applied_rules(rules, ctx)


# Rule configuration: declarative definition of all field clearing rules
def _build_production_unit_clearing_rules() -> list[FieldClearingRule]:
    """
    Build the list of field clearing rules for production unit instances.
    """
    from biomethane.models import BiomethaneProductionUnit

    return [
        # Clear sanitary approval number when sanitary approval is disabled
        FieldClearingRule(
            name="no_sanitary_approval",
            fields=BiomethaneProductionUnitService.SANITARY_APPROVAL_FIELDS,
            condition=lambda ctx: not ctx.instance.has_sanitary_approval,
        ),
        # Clear hygienization exemption type when hygienization exemption is disabled
        FieldClearingRule(
            name="no_hygienization_exemption",
            fields=BiomethaneProductionUnitService.HYGIENIZATION_EXEMPTION_FIELDS,
            condition=lambda ctx: not ctx.instance.has_hygienization_exemption,
        ),
        # Clear liquid/solid phase treatment steps when phase separation is disabled
        FieldClearingRule(
            name="no_phase_separation",
            fields=BiomethaneProductionUnitService.PHASE_SEPARATION_FIELDS,
            condition=lambda ctx: not ctx.instance.has_digestate_phase_separation,
        ),
        # Clear spreading management fields when SPREADING is not a valorization method
        FieldClearingRule(
            name="spreading_not_selected",
            fields=BiomethaneProductionUnitService.SPREADING_MANAGEMENT_FIELDS,
            condition=lambda ctx: BiomethaneProductionUnit.SPREADING
            not in (ctx.instance.digestate_valorization_methods or []),
        ),
        # Clear ISDND-related fields when unit_type is ISDND
        FieldClearingRule(
            name="isdnd",
            fields=BiomethaneProductionUnitService.ISDND_RELATED_FIELDS,
            condition=lambda ctx: (
                ctx.instance.unit_type == BiomethaneProductionUnit.ISDND
                or ctx.contract.installation_category == BiomethaneContract.INSTALLATION_CATEGORY_3
            ),
        ),
    ]


# Rule configuration: declarative definition of all optional fields rules
def _build_production_unit_optional_rules() -> list[FieldClearingRule]:
    """
    Build the list of optional fields rules for production unit instances.
    """
    from biomethane.models import BiomethaneProductionUnit

    return [
        # ICPE fields are optionals only when unit type is STEP
        OptionalFieldRule(
            name="STEP_unit_type",
            fields=BiomethaneProductionUnitService.ICPE_FIELDS,
            condition=lambda ctx: ctx.instance.unit_type == BiomethaneProductionUnit.STEP,
        ),
    ]
