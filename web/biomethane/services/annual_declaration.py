from datetime import date

from biomethane.models import (
    BiomethaneAnnualDeclaration,
    BiomethaneContract,
    BiomethaneDeclarationPeriod,
    BiomethaneDigestate,
    BiomethaneEnergy,
    BiomethaneProductionUnit,
    BiomethaneSupplyPlan,
)


class BiomethaneAnnualDeclarationService:
    @staticmethod
    def get_current_declaration_year():
        """
        Determines the current declaration year based on the current date.
        Always returns last year

        Returns:
            int: The year corresponding to the current declaration period.
        """
        today = date.today()
        return today.year - 1

    @staticmethod
    def is_declaration_period_open():
        """
        Check if we are currently in the declaration period.

        Returns:
            bool: True if current date is within the declaration period, False otherwise.
        """
        try:
            declaration_period = BiomethaneDeclarationPeriod.objects.get(
                year=BiomethaneAnnualDeclarationService.get_current_declaration_year()
            )
            return declaration_period.is_open
        except BiomethaneDeclarationPeriod.DoesNotExist:
            return False

    @staticmethod
    def get_declaration_status(declaration):
        """
        Returns the status of a biomethane annual declaration.

        If the declaration's year is earlier than the current declaration period and its status is not 'DECLARED',
        the method returns 'OVERDUE'. Otherwise, it returns the current status of the declaration.

        Args:
            declaration: An object representing the biomethane annual declaration.

        Returns:
            str: The status of the declaration, either 'OVERDUE' or its current status.
        """
        current_declaration_period = BiomethaneAnnualDeclarationService.get_current_declaration_year()

        if declaration.year < current_declaration_period and declaration.status != BiomethaneAnnualDeclaration.DECLARED:
            return BiomethaneAnnualDeclaration.OVERDUE

        return declaration.status

    @staticmethod
    def get_missing_fields(declaration):
        """
        Get the missing required fields for digestate, energy and supply plan declarations.

        Args:
            declaration: A BiomethaneAnnualDeclaration instance

        Returns:
            dict: Dictionary with 'digestate_missing_fields', 'energy_missing_fields', 'supply_plan_valid' keys.
                  Values are lists of missing field names or None if the model doesn't exist.
        """
        digestate = BiomethaneDigestate.objects.filter(producer=declaration.producer, year=declaration.year).first()
        energy = BiomethaneEnergy.objects.filter(producer=declaration.producer, year=declaration.year).first()
        supply_plan = BiomethaneSupplyPlan.objects.filter(producer=declaration.producer, year=declaration.year).first()

        return {
            "digestate_missing_fields": BiomethaneAnnualDeclarationService._get_missing_fields(digestate)
            if digestate
            else None,
            "energy_missing_fields": BiomethaneAnnualDeclarationService._get_missing_fields(energy) if energy else None,
            "supply_plan_valid": supply_plan and supply_plan.supply_inputs.exists(),
        }

    @staticmethod
    def _get_missing_fields(instance):
        """
        Return all missing fields for an instance.
        Takes into account optional fields defined by business rules.
        """
        all_fields = BiomethaneAnnualDeclarationService.get_all_fields(model=type(instance))

        optional_fields = instance.optional_fields if hasattr(instance, "optional_fields") else []
        required_fields = list(set(all_fields) - set(optional_fields))

        missing_fields = []
        for field in required_fields:
            value = getattr(instance, field, None)
            # Missing if None, empty string, or empty list
            if value is None or value == "" or value == []:
                missing_fields.append(field)

        return missing_fields

    @staticmethod
    def get_all_fields(model):
        """
        Return all field names for a given model.
        """
        if model is None:
            return []
        fields = []
        for field in model._meta.get_fields():
            fields.append(field.name)
        return fields

    @staticmethod
    def is_declaration_complete(declaration, missing_fields=None):
        """
        Check if the annual declaration is complete (all required fields are filled).

        Args:
            declaration: A BiomethaneAnnualDeclaration instance
            missing_fields: Optional dict of missing fields (will be computed if not provided)

        Returns:
            bool: True if digestate, energy and supply_plan are valid with no missing fields
        """
        if missing_fields is None:
            missing_fields = BiomethaneAnnualDeclarationService.get_missing_fields(declaration)

        return (
            missing_fields.get("digestate_missing_fields") is not None
            and len(missing_fields["digestate_missing_fields"]) == 0
            and missing_fields.get("energy_missing_fields") is not None
            and len(missing_fields["energy_missing_fields"]) == 0
            and missing_fields.get("supply_plan_valid") is True
        )

    @staticmethod
    def is_declaration_editable(producer, year):
        """
        Check if the annual declaration can be edited for a given producer and year.

        Args:
            producer: The Entity instance representing the producer
            year: The year of the declaration to check

        Returns:
            bool: True if declaration doesn't exist or status is not DECLARED, False otherwise
        """
        try:
            declaration = BiomethaneAnnualDeclaration.objects.get(producer=producer, year=year)
            return declaration.status != BiomethaneAnnualDeclaration.DECLARED
        except BiomethaneAnnualDeclaration.DoesNotExist:
            return True

    @staticmethod
    def get_watched_fields():
        """
        Return the list of fields from related models (production_unit, contract)
        that impact the conditional rules of an energy or digestate instance.

        Returns:
            dict: {
                'production_unit': list,  # Fields to watch on production_unit
                'contract': list,         # Fields to watch on contract
            }
        """
        PRODUCTION_UNIT_WATCHED_FIELDS = [
            "has_digestate_phase_separation",  # Impacts RAW_DIGESTATE_FIELDS vs SEPARATED_DIGESTATE_FIELDS
            "digestate_valorization_methods",  # Impacts SPREADING, INCINERATION, COMPOSTING fields
            "spreading_management_methods",  # Impacts SALE_FIELDS
        ]

        CONTRACT_WATCHED_FIELDS = [
            "tariff_reference",  # Impacts OLD_TARIFF_FIELDS and NEW_TARIFF_FIELDS
            "installation_category",  # Impacts WWTP_FIELDS
        ]

        return {
            "production_unit": PRODUCTION_UNIT_WATCHED_FIELDS,
            "contract": CONTRACT_WATCHED_FIELDS,
        }

    @staticmethod
    def has_watched_field_changed(instance, changed_fields):
        """
        Check if any watched field has changed on a production_unit or contract instance.

        Args:
            instance: A BiomethaneProductionUnit or BiomethaneContract instance
            changed_fields: List of field names that have changed

        Returns:
            bool: True if any watched field has changed, False otherwise

        """
        watched_fields = BiomethaneAnnualDeclarationService.get_watched_fields()

        if isinstance(instance, BiomethaneProductionUnit):
            return any(field in changed_fields for field in watched_fields["production_unit"])
        elif isinstance(instance, BiomethaneContract):
            return any(field in changed_fields for field in watched_fields["contract"])

        return False

    @staticmethod
    def reset_annual_declaration_status(producer):
        """
        Reset the current annual declaration status to IN_PROGRESS for a given producer.

        Args:
            producer: The Entity instance representing the producer
        """
        try:
            declaration = BiomethaneAnnualDeclaration.objects.get(
                producer=producer, year=BiomethaneAnnualDeclarationService.get_current_declaration_year()
            )
            if declaration.status != BiomethaneAnnualDeclaration.IN_PROGRESS:
                declaration.status = BiomethaneAnnualDeclaration.IN_PROGRESS
                declaration.save(update_fields=["status"])
        except BiomethaneAnnualDeclaration.DoesNotExist:
            pass
