from biomethane.models.biomethane_energy import BiomethaneEnergy


class BiomethaneEnergyService:
    """
    Centralized service to manage energy business logic.
    All validation rules and conditional field logic are defined here.
    """

    # Field groups definition (class constants)
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

    MALFUNCTION_FIELDS = [
        "malfunction_cumulative_duration_days",
        "malfunction_types",
        "malfunction_details",
    ]

    MALFUNCTION_DETAILS_FIELD = ["malfunction_details"]

    INJECTION_DIFFICULTY_FIELDS = ["injection_impossibility_hours"]

    @staticmethod
    def _extract_data(instance_or_data):
        """Extract data from an instance or a dictionary."""
        if isinstance(instance_or_data, dict):
            producer = instance_or_data.get("producer")
            has_malfunctions = instance_or_data.get("has_malfunctions", False)
            malfunction_types = instance_or_data.get("malfunction_types")
            has_injection_difficulties = instance_or_data.get("has_injection_difficulties_due_to_network_saturation", False)
            attest_no_fossil_for_digester_heating_and_purification = instance_or_data.get(
                "attest_no_fossil_for_digester_heating_and_purification", False
            )
            attest_no_fossil_for_installation_needs = instance_or_data.get("attest_no_fossil_for_installation_needs", False)
        else:
            producer = getattr(instance_or_data, "producer", None)
            has_malfunctions = getattr(instance_or_data, "has_malfunctions", False)
            malfunction_types = getattr(instance_or_data, "malfunction_types", None)
            has_injection_difficulties = getattr(
                instance_or_data, "has_injection_difficulties_due_to_network_saturation", False
            )
            attest_no_fossil_for_digester_heating_and_purification = getattr(
                instance_or_data, "attest_no_fossil_for_digester_heating_and_purification", False
            )
            attest_no_fossil_for_installation_needs = getattr(
                instance_or_data, "attest_no_fossil_for_installation_needs", False
            )

        production_unit = None
        contract = None
        if producer:
            production_unit = getattr(producer, "biomethane_production_unit", None)
            try:
                contract = producer.biomethane_contract
            except Exception:
                contract = None

        return (
            production_unit,
            contract,
            has_malfunctions,
            malfunction_types,
            has_injection_difficulties,
            attest_no_fossil_for_digester_heating_and_purification,
            attest_no_fossil_for_installation_needs,
        )

    @staticmethod
    def _apply_flaring_rules(production_unit, fields_to_clear):
        """Apply flaring rules based on installed meters."""
        from biomethane.models import BiomethaneProductionUnit

        installed_meters = production_unit.installed_meters if production_unit else []

        if BiomethaneProductionUnit.FLARING_FLOWMETER not in installed_meters:
            fields_to_clear.extend(BiomethaneEnergyService.FLARING_FIELDS)

    @staticmethod
    def _apply_tariff_rules(contract, fields_to_clear):
        """Apply rules based on contract tariff reference."""
        if not contract:
            return

        tariff_reference = getattr(contract, "tariff_reference", None)

        # Old tariff fields (2011, 2020, 2021)
        if tariff_reference not in ["2011", "2020", "2021"]:
            fields_to_clear.extend(BiomethaneEnergyService.OLD_TARIFF_FIELDS)

        # New tariff fields (2023)
        if tariff_reference not in ["2023"]:
            fields_to_clear.extend(BiomethaneEnergyService.NEW_TARIFF_FIELDS)

    @staticmethod
    def _apply_malfunction_rules(has_malfunctions, malfunction_types, fields_to_clear):
        """Apply rules based on malfunction status."""
        if not has_malfunctions:
            # No malfunctions → all malfunction fields are optional
            fields_to_clear.extend(BiomethaneEnergyService.MALFUNCTION_FIELDS)
        else:
            # Has malfunctions → check malfunction type
            if malfunction_types and malfunction_types != BiomethaneEnergy.MALFUNCTION_TYPE_OTHER:
                # Not "OTHER" type → details field is optional
                fields_to_clear.extend(BiomethaneEnergyService.MALFUNCTION_DETAILS_FIELD)

    @staticmethod
    def _apply_injection_difficulty_rules(has_injection_difficulties, fields_to_clear):
        """Apply rules based on injection difficulties status."""
        if not has_injection_difficulties:
            fields_to_clear.extend(BiomethaneEnergyService.INJECTION_DIFFICULTY_FIELDS)

    @staticmethod
    def _apply_installation_energy_needs_rules(
        attest_no_fossil_for_digester_heating_and_purification, attest_no_fossil_for_installation_needs, fields_to_clear
    ):
        """Apply rules based on installation energy needs status."""
        if attest_no_fossil_for_digester_heating_and_purification:
            fields_to_clear.extend(["fossil_details_for_digester_heating"])

        if attest_no_fossil_for_installation_needs:
            fields_to_clear.extend(["fossil_details_for_installation_needs"])

    @staticmethod
    def get_conditional_fields_rules(instance_or_data):
        """
        Return conditional field rules for an instance or data dictionary.

        Returns:
            dict: {
                'required_fields': list,  # Required fields based on business rules
                'fields_to_clear': list,  # Fields to clear/empty (also represents optional fields)
            }
        """
        required_fields = []
        fields_to_clear = []

        # Extract data
        (
            production_unit,
            contract,
            has_malfunctions,
            malfunction_types,
            has_injection_difficulties,
            attest_no_fossil_for_digester_heating_and_purification,
            attest_no_fossil_for_installation_needs,
        ) = BiomethaneEnergyService._extract_data(instance_or_data)

        # Apply rules based on production unit
        if production_unit:
            BiomethaneEnergyService._apply_flaring_rules(production_unit, fields_to_clear)

        # Apply rules based on contract
        if contract:
            BiomethaneEnergyService._apply_tariff_rules(contract, fields_to_clear)

        # Apply rules based on malfunction status
        BiomethaneEnergyService._apply_malfunction_rules(has_malfunctions, malfunction_types, fields_to_clear)

        # Apply rules based on injection difficulties
        BiomethaneEnergyService._apply_injection_difficulty_rules(has_injection_difficulties, fields_to_clear)

        # Apply rules based on installation energy needs
        BiomethaneEnergyService._apply_installation_energy_needs_rules(
            attest_no_fossil_for_digester_heating_and_purification, attest_no_fossil_for_installation_needs, fields_to_clear
        )
        return {
            "required_fields": list(set(required_fields)),
            "fields_to_clear": list(set(fields_to_clear)),
        }

    @staticmethod
    def get_optional_fields(instance):
        """
        Return the list of optional fields for a given instance.
        Used by the optional_fields property of the model.
        """
        rules = BiomethaneEnergyService.get_conditional_fields_rules(instance)
        return rules["fields_to_clear"]

    @staticmethod
    def get_required_fields(instance_or_data):
        """
        Return the list of required fields for an instance or data dictionary.
        Used for validation.
        """
        rules = BiomethaneEnergyService.get_conditional_fields_rules(instance_or_data)
        return rules["required_fields"]

    @staticmethod
    def get_fields_to_clear(instance):
        """
        Return the list of fields to clear for a given instance.
        Used by signals.
        """
        rules = BiomethaneEnergyService.get_conditional_fields_rules(instance)
        return rules["fields_to_clear"]
