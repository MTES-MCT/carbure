from collections import defaultdict
from dataclasses import dataclass

from biomethane.models import (
    BiomethaneContract,
    BiomethaneEnergy,
    BiomethaneEnergyMonthlyReport,
)

HOURS_PER_YEAR = 8760
PCS_KWH_PER_NM3_TO_GWH_FACTOR = 1e-6


def get_injected_biomethane_nm3_per_year(energy: BiomethaneEnergy | None) -> float | None:
    """Mirror front/src/biomethane/pages/energy/components/injected-biomethane/injected-biomethane.utils.ts."""
    if energy is None:
        return None

    gwh_pcs_per_year = energy.injected_biomethane_gwh_pcs_per_year
    pcs_kwh_per_nm3 = energy.injected_biomethane_pcs_kwh_per_nm3
    if gwh_pcs_per_year is None or pcs_kwh_per_nm3 is None:
        return None
    if pcs_kwh_per_nm3 == 0:
        return 0.0

    return round(gwh_pcs_per_year / (pcs_kwh_per_nm3 * PCS_KWH_PER_NM3_TO_GWH_FACTOR), 2)


def _total_injection_hours(monthly_reports: list[BiomethaneEnergyMonthlyReport]) -> float:
    total = 0.0
    for report in monthly_reports:
        average_flow = report.average_monthly_flow_nm3_per_hour or 0
        if average_flow == 0:
            continue
        total += (report.injected_volume_nm3 or 0) / average_flow
    return total


def get_operating_hours(
    energy: BiomethaneEnergy | None,
    contract: BiomethaneContract | None,
    monthly_reports: list[BiomethaneEnergyMonthlyReport],
) -> float | None:
    """Mirror front injected-biomethane hooks/utils (2011/2020 vs 2021/2023 tariff rules)."""
    if energy is None or contract is None:
        return None

    tariff_reference = contract.tariff_reference

    if tariff_reference in BiomethaneContract.TARIFF_RULE_1:
        injected_nm3_per_year = get_injected_biomethane_nm3_per_year(energy)
        cmax = contract.cmax
        if injected_nm3_per_year is None or not cmax:
            return None

        total_injection_hours = _total_injection_hours(monthly_reports)
        if total_injection_hours == 0:
            return None

        return round(HOURS_PER_YEAR * injected_nm3_per_year / (total_injection_hours * cmax), 0)

    if tariff_reference in BiomethaneContract.TARIFF_RULE_2:
        injected_gwh_pcs_per_year = energy.injected_biomethane_gwh_pcs_per_year
        pap_contracted = contract.pap_contracted
        if injected_gwh_pcs_per_year is None or not pap_contracted:
            return None

        return round(HOURS_PER_YEAR * injected_gwh_pcs_per_year / pap_contracted, 0)

    return None


@dataclass(frozen=True)
class EnergyMetrics:
    injected_biomethane_nm3_per_year: float | None
    operating_hours: float | None


def _preload_monthly_reports_by_energy_id(
    energy_ids: list[int],
) -> dict[int, list[BiomethaneEnergyMonthlyReport]]:
    if not energy_ids:
        return {}

    grouped = defaultdict(list)
    reports = BiomethaneEnergyMonthlyReport.objects.filter(energy_id__in=energy_ids).order_by("energy_id", "month")
    for report in reports:
        grouped[report.energy_id].append(report)
    return dict(grouped)


def preload_energy_metrics(
    energies: dict[int, BiomethaneEnergy],
    contracts_by_producer: dict[int, BiomethaneContract | None],
) -> dict[int, EnergyMetrics]:
    monthly_reports_by_energy_id = _preload_monthly_reports_by_energy_id([energy.id for energy in energies.values()])

    return {
        producer_id: EnergyMetrics(
            injected_biomethane_nm3_per_year=get_injected_biomethane_nm3_per_year(energy),
            operating_hours=get_operating_hours(
                energy,
                contracts_by_producer.get(producer_id),
                monthly_reports_by_energy_id.get(energy.id, []),
            ),
        )
        for producer_id, energy in energies.items()
    }
