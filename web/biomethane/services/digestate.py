from dataclasses import dataclass
from typing import Optional

from biomethane.models.biomethane_digestate import BiomethaneDigestate


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
            production_unit = getattr(producer, "biomethane_production_unit", None)
            try:
                contract = producer.biomethane_contract
            except Exception:
                contract = None

        # Return structured context
        return DigestateContext(
            instance=instance,
            production_unit=production_unit,
            contract=contract,
        )

    @staticmethod
    def _apply_phase_separation_rules(production_unit, fields_to_clear):
        """Apply digestate phase separation rules."""
        if production_unit.has_digestate_phase_separation:
            fields_to_clear.extend(BiomethaneDigestateService.RAW_DIGESTATE_FIELDS)
        else:
            fields_to_clear.extend(BiomethaneDigestateService.SEPARATED_DIGESTATE_FIELDS)

    @staticmethod
    def _apply_composting_rules(context: DigestateContext, required_fields, fields_to_clear):
        """Apply composting rules based on valorization methods and locations."""
        from biomethane.models import BiomethaneProductionUnit

        all_composting_fields = (
            BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS
            + BiomethaneDigestateService.ON_SITE_FIELDS
            + ["composting_locations"]
        )

        valorization_methods = (
            context.production_unit.digestate_valorization_methods or [] if context.production_unit else []
        )

        if BiomethaneProductionUnit.COMPOSTING not in valorization_methods:
            # Composting not enabled → all fields should be cleared
            fields_to_clear.extend(all_composting_fields)
        else:
            # Composting enabled → clear fields based on selected locations
            composting_locations = context.composting_locations

            # EXTERNAL_PLATFORM not selected → clear these fields
            if BiomethaneDigestate.EXTERNAL_PLATFORM not in composting_locations:
                fields_to_clear.extend(BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS)

            # ON_SITE not selected → clear these fields
            if BiomethaneDigestate.ON_SITE not in composting_locations:
                fields_to_clear.extend(BiomethaneDigestateService.ON_SITE_FIELDS)

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
    def _get_fields_to_clear(instance):
        """
        Return the list of fields to clear for a digestate instance.

        Returns:
            list: Fields to clear/empty (also represents optional fields)
        """
        fields_to_clear = []

        # Extract context
        context = BiomethaneDigestateService._extract_data(instance)

        # Apply rules based on production unit
        if context.production_unit:
            BiomethaneDigestateService._apply_phase_separation_rules(context.production_unit, fields_to_clear)

            BiomethaneDigestateService._apply_valorization_rules(context.production_unit, fields_to_clear)

            BiomethaneDigestateService._apply_composting_rules(context, [], fields_to_clear)

            BiomethaneDigestateService._apply_spreading_management_rules(context.production_unit, fields_to_clear)

        # Apply rules based on contract
        if context.contract:
            BiomethaneDigestateService._apply_contract_rules(context.contract, fields_to_clear)

        return list(set(fields_to_clear))

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
