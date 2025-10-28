from datetime import date

from django.utils.translation import gettext as _

from biomethane.models import BiomethaneContract
from biomethane.models.biomethane_contract_amendment import BiomethaneContractAmendment


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
        "general_conditions_file",
        "specific_conditions_file",
    ]

    @staticmethod
    def validate_tariff_reference(validated_data, errors):
        """Validate tariff reference is provided for contract creation."""
        if "tariff_reference" not in validated_data:
            errors["tariff_reference"] = [_("Ce champ est obligatoire pour la création d'un contrat.")]

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
    def get_required_fields_for_tariff(tariff_reference, required_fields):
        """
        Return required fields based on tariff reference.

        Returns:
            list: Required fields for the given tariff reference
        """
        # Tariff rule 1
        if tariff_reference in BiomethaneContract.TARIFF_RULE_1:
            required_fields.extend(BiomethaneContractService.TARIFF_RULE_1_FIELDS)

        # Tariff rule 2
        elif tariff_reference in BiomethaneContract.TARIFF_RULE_2:
            required_fields.extend(BiomethaneContractService.TARIFF_RULE_2_FIELDS)

    @staticmethod
    def validate_tariff_rule_1_specific(validated_data, required_fields):
        """Validate specific rules for tariff rule 1."""
        cmax_annualized = validated_data.get("cmax_annualized")

        if cmax_annualized:
            required_fields.append("cmax_annualized_value")

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
        # 2011 : 23/11/2011 et 23/11/2020
        if tariff_reference == "2011" and not (
            signature_date >= date(2011, 11, 23) and signature_date <= date(2020, 11, 23)
        ):
            errors["signature_date"] = [
                _(
                    (
                        "Pour la référence tarifaire 2011, la date de signature doit être entre "
                        "le 23/11/2011 et le 23/11/2020."
                    )
                )
            ]

        # 2020 : 23/11/2020 et 13/12/2021
        if tariff_reference == "2020" and not (
            signature_date >= date(2020, 11, 23) and signature_date <= date(2021, 12, 13)
        ):
            errors["signature_date"] = [
                _(
                    (
                        "Pour la référence tarifaire 2020, la date de signature doit être entre "
                        "le 23/11/2020 et le 13/12/2021."
                    )
                )
            ]

        # 2021, 13/12/2021 et 10/06/2023
        if tariff_reference == "2021" and not (signature_date >= date(2021, 12, 13) and signature_date <= date(2023, 6, 10)):
            errors["signature_date"] = [
                _(
                    (
                        "Pour la référence tarifaire 2021, la date de signature doit être entre "
                        "le 13/12/2021 et le 10/06/2023."
                    )
                )
            ]

        # 2023, date de signature > 10/06/2023
        if tariff_reference == "2023" and not (signature_date and signature_date > date(2023, 6, 10)):
            errors["signature_date"] = [
                _("Pour la référence tarifaire 2023, la date de signature doit être postérieure au 10/06/2023.")
            ]

    @staticmethod
    def get_required_fields_for_contract_document(validated_data, required_fields):
        """
        Return all contract document fields as required if any of them is provided.

        Returns:
            list: Contract document fields if any is provided, empty list otherwise
        """
        for field in BiomethaneContractService.CONTRACT_DOCUMENT_FIELDS:
            if field in validated_data:
                required_fields.extend(BiomethaneContractService.CONTRACT_DOCUMENT_FIELDS)
                break

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

        # Validate tariff reference for contract creation
        if not contract:
            BiomethaneContractService.validate_tariff_reference(validated_data, errors)

        # Validate contract document fields
        BiomethaneContractService.validate_contract_document_fields(contract, validated_data, errors)

        # Get required fields for contract document
        BiomethaneContractService.get_required_fields_for_contract_document(validated_data, required_fields)

        # Get required fields based on tariff reference
        if tariff_reference:
            BiomethaneContractService.get_required_fields_for_tariff(tariff_reference, required_fields)

            # Validate tariff rule 1 specific rules
            if tariff_reference in BiomethaneContract.TARIFF_RULE_1:
                BiomethaneContractService.validate_tariff_rule_1_specific(validated_data, required_fields)

        # Validate contract dates
        signature_date = validated_data.get("signature_date")
        effective_date = validated_data.get("effective_date")
        if tariff_reference:
            BiomethaneContractService.validate_contract_dates(signature_date, effective_date, tariff_reference, errors)

        return errors, required_fields

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
        fields_to_clear = []

        # Clear fields based on tariff reference rules
        if contract.tariff_reference in BiomethaneContract.TARIFF_RULE_1:
            fields_to_clear.append("pap_contracted")
        elif contract.tariff_reference in BiomethaneContract.TARIFF_RULE_2:
            fields_to_clear.extend(["cmax_annualized", "cmax_annualized_value", "cmax"])

        # Clear cmax_annualized_value if cmax_annualized is explicitly set to False
        # and it's not already in the list to be cleared
        if contract.cmax_annualized is False and "cmax_annualized_value" not in fields_to_clear:
            fields_to_clear.append("cmax_annualized_value")

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

        # Track CMAX/PAP updates
        if contract.cmax != validated_data.get("cmax", None) or contract.pap_contracted != validated_data.get(
            "pap_contracted", None
        ):
            current_tracked_types.add(BiomethaneContractAmendment.CMAX_PAP_UPDATE)

        # Track CMAX annualization changes
        if contract.cmax_annualized != validated_data.get("cmax_annualized", False):
            current_tracked_types.add(BiomethaneContractAmendment.CMAX_ANNUALIZATION)

        # Track buyer changes
        if validated_buyer is not None and contract.buyer != validated_buyer:
            current_tracked_types.add(BiomethaneContractAmendment.PRODUCER_BUYER_INFO_CHANGE)

        result = list(current_tracked_types)
        result.sort()

        return result
