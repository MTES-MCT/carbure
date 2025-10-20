from biomethane.models.biomethane_digestate import BiomethaneDigestate


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
    def _extract_data(instance_or_data):
        """Extract data from an instance or a dictionary."""
        if isinstance(instance_or_data, dict):
            composting_locations = instance_or_data.get("composting_locations", [])
            producer = instance_or_data.get("producer")
        else:
            composting_locations = getattr(instance_or_data, "composting_locations", []) or []
            producer = getattr(instance_or_data, "producer", None)

        production_unit = None
        contract = None
        if producer:
            production_unit = getattr(producer, "biomethane_production_unit", None)
            try:
                contract = producer.biomethane_contract
            except Exception:
                contract = None

        return composting_locations, production_unit, contract

    @staticmethod
    def _apply_phase_separation_rules(production_unit, fields_to_clear):
        """Apply digestate phase separation rules."""
        if production_unit.has_digestate_phase_separation:
            fields_to_clear.extend(BiomethaneDigestateService.RAW_DIGESTATE_FIELDS)
        else:
            fields_to_clear.extend(BiomethaneDigestateService.SEPARATED_DIGESTATE_FIELDS)

    @staticmethod
    def _apply_composting_rules(valorization_methods, composting_locations, required_fields, fields_to_clear):
        """Apply composting rules based on valorization methods and locations."""
        from biomethane.models import BiomethaneProductionUnit

        all_composting_fields = (
            BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS
            + BiomethaneDigestateService.ON_SITE_FIELDS
            + ["composting_locations"]
        )

        if BiomethaneProductionUnit.COMPOSTING not in valorization_methods:
            # Composting not enabled → all fields are optional
            fields_to_clear.extend(all_composting_fields)
            # Remove from required fields if already added
            required_fields[:] = [f for f in required_fields if f not in all_composting_fields]
        else:
            # Composting enabled → apply location rules
            BiomethaneDigestateService._apply_composting_location_rules(
                composting_locations, required_fields, fields_to_clear
            )

    @staticmethod
    def _apply_composting_location_rules(composting_locations, required_fields, fields_to_clear):
        """Apply rules based on selected composting locations."""
        if composting_locations:
            # EXTERNAL_PLATFORM selected?
            if BiomethaneDigestate.EXTERNAL_PLATFORM in composting_locations:
                required_fields.extend(BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS)
            else:
                fields_to_clear.extend(BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS)

            # ON_SITE selected?
            if BiomethaneDigestate.ON_SITE in composting_locations:
                required_fields.extend(BiomethaneDigestateService.ON_SITE_FIELDS)
            else:
                fields_to_clear.extend(BiomethaneDigestateService.ON_SITE_FIELDS)
        else:
            # No location selected → all location fields are optional
            fields_to_clear.extend(
                BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS + BiomethaneDigestateService.ON_SITE_FIELDS
            )

    @staticmethod
    def _apply_valorization_rules(production_unit, fields_to_clear):
        """Apply rules based on valorization methods."""
        from biomethane.models import BiomethaneProductionUnit

        valorization_methods = production_unit.digestate_valorization_methods or []

        # Spreading
        if BiomethaneProductionUnit.SPREADING not in valorization_methods:
            fields_to_clear.extend(BiomethaneDigestateService.SPREADING_FIELDS)

        # Incineration / Landfilling
        if BiomethaneProductionUnit.INCINERATION_LANDFILLING not in valorization_methods:
            fields_to_clear.extend(BiomethaneDigestateService.INCINERATION_FIELDS + BiomethaneDigestateService.WWTP_FIELDS)

    @staticmethod
    def _apply_spreading_management_rules(production_unit, fields_to_clear):
        """Apply rules based on spreading management methods."""
        from biomethane.models import BiomethaneProductionUnit

        spreading_management_methods = production_unit.spreading_management_methods or []
        if BiomethaneProductionUnit.SALE not in spreading_management_methods:
            fields_to_clear.extend(BiomethaneDigestateService.SALE_FIELDS)

    @staticmethod
    def _apply_contract_rules(contract, fields_to_clear):
        """Apply rules based on contract."""
        from biomethane.models import BiomethaneContract

        if contract.installation_category != BiomethaneContract.INSTALLATION_CATEGORY_2:
            fields_to_clear.extend(BiomethaneDigestateService.WWTP_FIELDS)

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
        composting_locations, production_unit, contract = BiomethaneDigestateService._extract_data(instance_or_data)

        # Apply rules based on production unit
        if production_unit:
            BiomethaneDigestateService._apply_phase_separation_rules(production_unit, fields_to_clear)

            BiomethaneDigestateService._apply_valorization_rules(production_unit, fields_to_clear)

            valorization_methods = production_unit.digestate_valorization_methods or []

            BiomethaneDigestateService._apply_composting_rules(
                valorization_methods, composting_locations, required_fields, fields_to_clear
            )

            BiomethaneDigestateService._apply_spreading_management_rules(production_unit, fields_to_clear)
        else:
            # No production unit → apply basic composting rules only
            BiomethaneDigestateService._apply_composting_location_rules(
                composting_locations, required_fields, fields_to_clear
            )

        # Apply rules based on contract
        if contract:
            BiomethaneDigestateService._apply_contract_rules(contract, fields_to_clear)

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
        rules = BiomethaneDigestateService.get_conditional_fields_rules(instance)
        return rules["fields_to_clear"]

    @staticmethod
    def get_required_fields(instance_or_data):
        """
        Return the list of required fields for an instance or data dictionary.
        Used for validation.
        """
        rules = BiomethaneDigestateService.get_conditional_fields_rules(instance_or_data)
        return rules["required_fields"]

    @staticmethod
    def get_fields_to_clear(instance):
        """
        Return the list of fields to clear for a given instance.
        Used by signals.
        """
        rules = BiomethaneDigestateService.get_conditional_fields_rules(instance)
        return rules["fields_to_clear"]
