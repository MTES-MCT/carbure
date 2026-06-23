from django.db.models import Q

from biomethane.models import BiomethaneContract


class AdemeService:
    @staticmethod
    def get_ademe_min_effective_year() -> int:
        """
        ADEME sees declarations for the first five years of the installation.
        """
        from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService

        current_declaration_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        return current_declaration_year - 4

    @staticmethod
    def get_ademe_contract_filter(contract_prefix: str) -> Q:
        """
        ADEME only sees data for the first five years of the installation.
        Ex : effective_date is 02/04/2023, ADEME will see the data for the years 2023 to 2027
        """
        min_effective_year = AdemeService.get_ademe_min_effective_year()
        return Q(
            **{
                f"{contract_prefix}complementary_aid_organisms__contains": [
                    BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME
                ],
                f"{contract_prefix}effective_date__year__gte": min_effective_year,
            }
        )

    # Get contract from any object related to biomethane
    @staticmethod
    def get_contract_from_object(obj):
        if isinstance(obj, BiomethaneContract):
            return obj

        producer = getattr(obj, "producer", None)
        contract = getattr(producer, "biomethane_contract", None) if producer else None

        return contract

    # Check if any object related to biomethane is allowed to be accessed by ADEME
    @staticmethod
    def is_allowed_to_access_object(obj):
        min_effective_year = AdemeService.get_ademe_min_effective_year()
        contract = AdemeService.get_contract_from_object(obj)

        if contract is None:
            return False

        return (
            contract.complementary_aid_organisms is not None
            and BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME in contract.complementary_aid_organisms
            and contract.effective_date.year >= min_effective_year
        )
