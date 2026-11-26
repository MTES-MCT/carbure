"""
Declaration data exposed to biomethane gas providers.
"""

from biomethane.models import BiomethaneAnnualDeclaration, BiomethaneEnergy


def get_provider_declarations(provider):
    """Annual declarations (any status) of the producers that have a contract with the provider."""
    return (
        BiomethaneAnnualDeclaration.annotated_objects.filter(producer__biomethane_contract__buyer=provider)
        .select_related("producer__biomethane_contract")
        .select_related("producer__biomethane_production_unit")
        .order_by("year", "producer__name", "id")
    )


def get_declaration_energy_values(declarations):
    """Fetch energy data for declaration producers and years in a single query."""
    declarations = list(declarations)
    energies = BiomethaneEnergy.objects.filter(
        producer_id__in={item.producer_id for item in declarations},
        year__in={item.year for item in declarations},
    ).values(
        "producer_id",
        "year",
        "purification_electric_consumption_kwe",
        "purified_biogas_quantity_nm3",
        "total_unit_electric_consumption_kwe",
        "injected_biomethane_gwh_pcs_per_year",
    )
    return {(energy["producer_id"], energy["year"]): energy for energy in energies}


def get_declaration_energy_metrics(declaration, energies):
    """Calculate consumption and efficiency using the declaration's tariff and energy data."""
    energy = energies.get((declaration.producer_id, declaration.year))
    tariff = declaration.producer.biomethane_contract.tariff_reference
    if not energy:
        return 0.0, 0.0
    if tariff in ("2011", "2020", "2021"):
        consumption = energy["purification_electric_consumption_kwe"] or 0.0
        quantity = energy["purified_biogas_quantity_nm3"] or 0.0
        return consumption, consumption / quantity if quantity else 0.0
    if tariff == "2023":
        consumption = energy["total_unit_electric_consumption_kwe"] or 0.0
        quantity = energy["injected_biomethane_gwh_pcs_per_year"] or 0.0
        return consumption, consumption / quantity * 1e-6 if quantity else 0.0
    return 0.0, 0.0
