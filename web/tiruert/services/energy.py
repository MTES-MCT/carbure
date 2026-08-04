from django.db.models import ExpressionWrapper, FloatField, Value


def energy_mj(volume, pci_litre, renewable_energy_share=1.0):
    """Compute energy in MJ from volume in liters."""
    return volume * renewable_energy_share * pci_litre


def energy_mj_expression(
    volume_expr,
    renewable_energy_share_expr,
    pci_litre_expr,
    sign_expr=None,
):
    """Build a SQL expression for energy in MJ."""
    expression = volume_expr * renewable_energy_share_expr * pci_litre_expr
    if sign_expr is not None:
        expression = expression * sign_expr
    return ExpressionWrapper(expression, output_field=FloatField())


def tco2_from_mj(energy_mj_value, factor_gco2_per_mj):
    """Convert energy (MJ) to tCO2 using a gCO2/MJ factor."""
    return energy_mj_value * factor_gco2_per_mj / 1_000_000


def tco2_from_mj_expression(energy_expr, factor_gco2_per_mj):
    """Build a SQL expression converting MJ to tCO2."""
    return ExpressionWrapper(
        energy_expr * Value(factor_gco2_per_mj) / Value(1_000_000.0),
        output_field=FloatField(),
    )


def avoided_emissions_tco2(energy_mj_value, emission_rate_per_mj, ghg_reference_per_mj):
    """Compute avoided emissions in tCO2 from energy and emission rate."""
    return (ghg_reference_per_mj - emission_rate_per_mj) * energy_mj_value / 1_000_000


def avoided_emissions_tco2_expression(energy_expr, emission_rate_expr, ghg_reference_per_mj):
    """Build a SQL expression computing avoided emissions in tCO2."""
    return ExpressionWrapper(
        (Value(ghg_reference_per_mj) - emission_rate_expr) * energy_expr / Value(1_000_000.0),
        output_field=FloatField(),
    )
