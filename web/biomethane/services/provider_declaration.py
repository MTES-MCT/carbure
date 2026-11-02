"""
Declaration data exposed to biomethane gas providers.
"""

from biomethane.models import BiomethaneAnnualDeclaration


def get_provider_declarations(provider):
    """Annual declarations (any status) of the producers that have a contract with the provider."""
    return (
        BiomethaneAnnualDeclaration.annotated_objects.filter(producer__biomethane_contract__buyer=provider)
        .select_related("producer__biomethane_contract")
        .select_related("producer__biomethane_production_unit")
        .order_by("year", "producer__name", "id")
    )
