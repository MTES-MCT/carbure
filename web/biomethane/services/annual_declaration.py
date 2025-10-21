from biomethane.models import (
    BiomethaneContract,
    BiomethaneDigestate,
    BiomethaneEnergy,
    BiomethaneProductionUnit,
)
from biomethane.models.biomethane_annual_declaration import BiomethaneAnnualDeclaration
from biomethane.utils import get_declaration_period


class BiomethaneAnnualDeclarationService:
    @staticmethod
    def get_missing_fields(declaration):
        digestat_missing_fields = []
        energy_missing_fields = []

        try:
            digestat = BiomethaneDigestate.objects.get(producer=declaration.producer, year=declaration.year)
        except BiomethaneDigestate.DoesNotExist:
            digestat = None

        try:
            energy = BiomethaneEnergy.objects.get(producer=declaration.producer, year=declaration.year)
        except BiomethaneEnergy.DoesNotExist:
            energy = None

        if digestat is not None:
            digestat_missing_fields = BiomethaneAnnualDeclarationService._get_missing_fields(digestat)

        if energy is not None:
            energy_missing_fields = BiomethaneAnnualDeclarationService._get_missing_fields(energy)

        return {
            "digestate_missing_fields": digestat_missing_fields,
            "energy_missing_fields": energy_missing_fields,
        }

    @staticmethod
    def _get_missing_fields(instance):
        """
        Return all missing fields for an instance.
        Takes into account optional fields defined by business rules.
        """
        all_fields = BiomethaneAnnualDeclarationService.get_required_fields(model=type(instance))

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
    def get_required_fields(model):
        if model is None:
            return []
        fields = []
        for field in model._meta.get_fields():
            fields.append(field.name)
        return fields

    @staticmethod
    def is_declaration_complete(declaration):
        missing_fields = BiomethaneAnnualDeclarationService.get_missing_fields(declaration)
        return len(missing_fields["digestate_missing_fields"]) == 0 and len(missing_fields["energy_missing_fields"]) == 0

    @staticmethod
    def is_declaration_editable(producer, year):
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
            "installed_meters",  # Impacts FLARING_FIELDS
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
        Reset the annual declaration status to IN_PROGRESS for a given producer and year.

        Args:
            producer: The Entity instance representing the producer
            year: The year of the declaration to reset

        """
        try:
            declaration = BiomethaneAnnualDeclaration.objects.get(producer=producer, year=get_declaration_period())
            if declaration.status != BiomethaneAnnualDeclaration.IN_PROGRESS:
                declaration.status = BiomethaneAnnualDeclaration.IN_PROGRESS
                declaration.save(update_fields=["status"])
        except BiomethaneAnnualDeclaration.DoesNotExist:
            pass
