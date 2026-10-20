"""
Declaration data exposed to biomethane gas providers.
"""

from biomethane.models import BiomethaneAnnualDeclaration


def get_provider_declarations(provider):
    """Validated annual declarations of the producers that have a contract with the provider."""
    return (
        BiomethaneAnnualDeclaration.objects.filter(
            status=BiomethaneAnnualDeclaration.DECLARED,
            producer__biomethane_contract__buyer=provider,
        )
        .select_related("producer__biomethane_contract")
        .select_related("producer__biomethane_production_unit")
        .order_by("year", "producer__name", "id")
    )
