from dataclasses import dataclass
from datetime import date

from django.utils.translation import gettext as _

from biomethane.models import BiomethaneContract
from biomethane.models.biomethane_contract_amendment import BiomethaneContractAmendment
from biomethane.services.rules import FieldClearingRule, RequiredFieldRule, get_fields_from_applied_rules


@dataclass
class ContractValidationContext:
    """Context object for contract validation rules."""

    is_creation: bool
    tariff_reference: str | None
    cmax_annualized: bool | None
    has_contract_document: bool
    has_complementary_investment_aid: bool | None
    complementary_aid_organisms: list[str] | None

    @classmethod
    def from_contract_and_data(cls, contract, validated_data):
        """
        Factory method to create context from contract and validated data.

        Args:
            contract: The contract instance (None for creation)
            validated_data: The validated data dictionary

        Returns:
            ContractValidationContext instance
        """
        return cls(
            is_creation=contract is None,
            tariff_reference=validated_data.get("tariff_reference"),
            cmax_annualized=validated_data.get("cmax_annualized"),
            has_complementary_investment_aid=validated_data.get("has_complementary_investment_aid"),
            complementary_aid_organisms=validated_data.get("complementary_aid_organisms"),
            has_contract_document=any(
                field in validated_data for field in BiomethaneContractService.CONTRACT_DOCUMENT_FIELDS
            ),
        )


class BiomethaneContractService:
    """
    Centralized service to manage contract business logic.
    All validation rules and conditional field logic are defined here.
    """

    # Field groups definition (class constants)
    TARIFF_RULE_1_FIELDS = ["cmax", "cmax_annualized", "installation_category", "buyer"]
    TARIFF_RULE_2_FIELDS = ["pap_contracted", "installation_category", "buyer"]
    CONTRACT_DOCUMENT_FIELDS = [
        "signature_date",
        "effective_date",
        "conditions_file",
    ]

    # Tariff date ranges for signature validation: (start_date, end_date, error_message)
    TARIFF_DATE_RANGES = {
        "2011": (
            date(2011, 11, 23),
            date(2020, 11, 23),
            _("Pour la référence tarifaire 2011, la date de signature doit être entre le 23/11/2011 et le 23/11/2020."),
        ),
        "2020": (
            date(2020, 11, 23),
            date(2021, 12, 13),
            _("Pour la référence tarifaire 2020, la date de signature doit être entre le 23/11/2020 et le 13/12/2021."),
        ),
        "2021": (
            date(2021, 12, 13),
            date(2023, 6, 10),
            _("Pour la référence tarifaire 2021, la date de signature doit être entre le 13/12/2021 et le 10/06/2023."),
        ),
    }

    @staticmethod
    def validate_contract_document_fields(contract, validated_data, errors):
        """Validate that contract document fields cannot be updated after contract signing."""
        if contract and contract.does_contract_exist():
            not_updatable_fields = [
                field for field in BiomethaneContractService.CONTRACT_DOCUMENT_FIELDS if field in validated_data
            ]
            for field in not_updatable_fields:
                errors[field] = [_(f"Le champ {field} ne peut pas être modifié une fois le contrat signé.")]

    @staticmethod
    def validate_contract_dates(signature_date, effective_date, tariff_reference, errors):
        """Validate contract dates logic."""
        if not (signature_date and effective_date):
            return

        # Effective date must be after signature date
        if effective_date <= signature_date:
            errors["effective_date"] = [_("La date d'effet doit être postérieure à la date de signature.")]

        # Validate signature date based on tariff reference
        BiomethaneContractService._validate_signature_date_by_tariff(signature_date, tariff_reference, errors)

    @staticmethod
    def _validate_signature_date_by_tariff(signature_date, tariff_reference, errors):
        """Validate signature date based on tariff reference."""
        # Check date range for tariffs with specific periods
        if tariff_reference in BiomethaneContractService.TARIFF_DATE_RANGES:
            start_date, end_date, error_message = BiomethaneContractService.TARIFF_DATE_RANGES[tariff_reference]
            if not (signature_date >= start_date and signature_date <= end_date):
                errors["signature_date"] = [error_message]

        # 2023: date de signature > 10/06/2023 (no upper bound)
        elif tariff_reference == "2023" and not (signature_date and signature_date > date(2023, 6, 10)):
            errors["signature_date"] = [
                _("Pour la référence tarifaire 2023, la date de signature doit être postérieure au 10/06/2023.")
            ]

    @staticmethod
    def validate_contract(contract, validated_data):
        """
        Main validation method for contract data.

        Args:
            contract: The contract instance (None for creation)
            validated_data: The data to validate

        Returns:
            tuple: (errors, required_fields)
        """
        errors = {}
        required_fields = []

        tariff_reference = validated_data.get("tariff_reference")
        # Get required fields using rule engine
        required_fields.extend(BiomethaneContractService.get_required_fields(contract, validated_data))

        # Validate contract document fields
        BiomethaneContractService.validate_contract_document_fields(contract, validated_data, errors)

        # Validate contract dates
        signature_date = validated_data.get("signature_date")
        effective_date = validated_data.get("effective_date")
        if tariff_reference:
            BiomethaneContractService.validate_contract_dates(signature_date, effective_date, tariff_reference, errors)

        return errors, required_fields

    @staticmethod
    def get_required_fields(contract, validated_data):
        """
        Determine required fields based on validated data using rule engine.

        Args:
            contract: The contract instance (None for creation)
            validated_data: The data to validate

        Returns:
            list: List of required field names
        """
        # Build context for rules
        context = ContractValidationContext.from_contract_and_data(contract, validated_data)

        # Get all required field rules
        rules = _build_required_field_rules()

        # Evaluate rules and collect required fields
        required_fields = get_fields_from_applied_rules(rules, context)

        return required_fields

    @staticmethod
    def handle_is_red_ii(validated_data, producer):
        """
        Handle is_red_ii logic based on cmax and pap_contracted thresholds.

        Args:
            validated_data: The validated data
            producer: The producer entity
        """
        is_red_ii = validated_data.pop("is_red_ii", None)
        cmax = validated_data.get("cmax", None)
        pap_contracted = validated_data.get("pap_contracted", None)

        # If cmax or pap_contracted is below the threshold and
        # the user does not want to be subject to RED II, then is_red_ii is set to False
        if is_red_ii is False and ((cmax and cmax <= 200) or (pap_contracted and pap_contracted <= 19.5)):
            producer.is_red_ii = is_red_ii
            producer.save(update_fields=["is_red_ii"])

    @staticmethod
    def clear_fields_based_on_tariff(contract):
        """
        Clear specific contract fields based on tariff reference and boolean values.

        This method determines which fields should be cleared based on the tariff rules:
        - TARIFF_RULE_1 (2011, 2020): clears pap_contracted
        - TARIFF_RULE_2 (2021, 2023): clears cmax, cmax_annualized, cmax_annualized_value
        - When cmax_annualized is False: clears cmax_annualized_value

        Args:
            contract: The BiomethaneContract instance to update

        Returns:
            dict: Dictionary of fields to update with their new values
        """
        # Get all clearing rules
        rules = _build_contract_clearing_rules()

        # Evaluate rules and collect fields to clear
        fields_to_clear = get_fields_from_applied_rules(rules, contract)

        # Build update dictionary
        update_data = {}
        if fields_to_clear:
            for field in fields_to_clear:
                # Special case: cmax_annualized should be set to False, not None
                new_value = False if field == "cmax_annualized" else None
                update_data[field] = new_value

        return update_data

    @staticmethod
    def get_tracked_amendment_types(contract, validated_data):
        """
        Determine which amendment types should be tracked based on contract changes.

        This method compares the current contract values with the validated data
        to identify which types of amendments need to be tracked for regulatory purposes.

        Args:
            contract: The BiomethaneContract instance being updated
            validated_data: The new validated data to be applied

        Returns:
            list: Sorted list of amendment types (from BiomethaneContractAmendment) to track
        """
        current_tracked_types = set(contract.tracked_amendment_types or [])
        validated_buyer = validated_data.get("buyer", None)
        cmax = validated_data.get("cmax", None)
        pap_contracted = validated_data.get("pap_contracted", None)
        cmax_annualized = validated_data.get("cmax_annualized")

        # Track CMAX/PAP updates
        if (cmax is not None and contract.cmax != cmax) or (
            pap_contracted is not None and contract.pap_contracted != pap_contracted
        ):
            current_tracked_types.add(BiomethaneContractAmendment.CMAX_PAP_UPDATE)

        # Track CMAX annualization changes
        if cmax_annualized is not None and contract.cmax_annualized != cmax_annualized:
            current_tracked_types.add(BiomethaneContractAmendment.CMAX_ANNUALIZATION)

        # Track buyer changes
        if validated_buyer is not None and contract.buyer != validated_buyer:
            current_tracked_types.add(BiomethaneContractAmendment.PRODUCER_BUYER_INFO_CHANGE)

        result = list(current_tracked_types)
        result.sort()

        return result


# Rule configuration: declarative definition of field clearing rules
def _build_contract_clearing_rules() -> list[FieldClearingRule]:
    """
    Build the list of field clearing rules for contract instances.
    """
    return [
        # TARIFF_RULE_1 (2011, 2020): clear pap_contracted
        FieldClearingRule(
            name="tariff_rule_1_clear_pap",
            fields=["pap_contracted"],
            condition=lambda contract: contract.tariff_reference in BiomethaneContract.TARIFF_RULE_1,
        ),
        # TARIFF_RULE_2 (2021, 2023): clear cmax fields
        FieldClearingRule(
            name="tariff_rule_2_clear_cmax",
            fields=["cmax", "cmax_annualized", "cmax_annualized_value"],
            condition=lambda contract: contract.tariff_reference in BiomethaneContract.TARIFF_RULE_2,
        ),
        # Clear cmax_annualized_value when cmax_annualized is False
        FieldClearingRule(
            name="cmax_not_annualized",
            fields=["cmax_annualized_value"],
            condition=lambda contract: contract.cmax_annualized is False,
        ),
        FieldClearingRule(
            name="complementary_aid_organisms_disabled",
            fields=["complementary_aid_organisms", "complementary_aid_other_organism_name"],
            condition=lambda contract: contract.has_complementary_investment_aid is False,
        ),
        FieldClearingRule(
            name="complementary_aid_other_organism_name_not_selected",
            fields=["complementary_aid_other_organism_name"],
            condition=lambda contract: (
                contract.complementary_aid_organisms
                and BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_OTHER not in contract.complementary_aid_organisms
            ),
        ),
    ]


# Rule configuration: declarative definition of required field rules
def _build_required_field_rules() -> list[RequiredFieldRule]:
    """
    Build the list of required field rules for contract validation.
    """
    return [
        # Contract creation: tariff_reference is required
        RequiredFieldRule(
            name="tariff_reference_on_creation",
            fields=["tariff_reference"],
            condition=lambda ctx: ctx.is_creation,
        ),
        # TARIFF_RULE_1 (2011, 2020): require specific fields
        RequiredFieldRule(
            name="tariff_rule_1_required",
            fields=BiomethaneContractService.TARIFF_RULE_1_FIELDS,
            condition=lambda ctx: ctx.tariff_reference in BiomethaneContract.TARIFF_RULE_1,
        ),
        # TARIFF_RULE_2 (2021, 2023): require specific fields
        RequiredFieldRule(
            name="tariff_rule_2_required",
            fields=BiomethaneContractService.TARIFF_RULE_2_FIELDS,
            condition=lambda ctx: ctx.tariff_reference in BiomethaneContract.TARIFF_RULE_2,
        ),
        # When cmax_annualized is True: require cmax_annualized_value
        RequiredFieldRule(
            name="cmax_annualized_requires_value",
            fields=["cmax_annualized_value"],
            condition=lambda ctx: ctx.cmax_annualized is True and ctx.tariff_reference in BiomethaneContract.TARIFF_RULE_1,
        ),
        # When any contract document field is provided: require all document fields
        RequiredFieldRule(
            name="contract_document_all_or_nothing",
            fields=BiomethaneContractService.CONTRACT_DOCUMENT_FIELDS,
            condition=lambda ctx: ctx.has_contract_document,
        ),
        # When has_complementary_investment_aid is True: require complementary_aid_organisms
        RequiredFieldRule(
            name="complementary_aid_organisms_required",
            fields=["complementary_aid_organisms"],
            condition=lambda ctx: ctx.has_complementary_investment_aid is True,
        ),
        # When has_complementary_investment_aid is True: require complementary_aid_other_organism_name
        RequiredFieldRule(
            name="complementary_aid_other_organism_name_required",
            fields=["complementary_aid_other_organism_name"],
            condition=lambda ctx: ctx.has_complementary_investment_aid is True
            and BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_OTHER in ctx.complementary_aid_organisms,
        ),
    ]
