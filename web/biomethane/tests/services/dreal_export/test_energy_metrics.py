from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models import BiomethaneContract, BiomethaneEnergy, BiomethaneEnergyMonthlyReport
from biomethane.services.dreal_export.metrics.energy import (
    get_injected_biomethane_nm3_per_year,
    get_operating_hours,
    preload_energy_metrics,
)
from core.models import Entity


def _energy(**kwargs) -> BiomethaneEnergy:
    return BiomethaneEnergy(
        producer=Entity(name="Producer"),
        year=2024,
        **kwargs,
    )


def _monthly_report(**kwargs) -> BiomethaneEnergyMonthlyReport:
    kwargs.setdefault("month", 1)
    return BiomethaneEnergyMonthlyReport(**kwargs)


class GetInjectedBiomethaneNm3PerYearTests(TestCase):
    def test_returns_none_when_energy_is_missing(self):
        self.assertIsNone(get_injected_biomethane_nm3_per_year(None))

    def test_returns_none_when_required_fields_are_missing(self):
        self.assertIsNone(get_injected_biomethane_nm3_per_year(_energy()))
        self.assertIsNone(
            get_injected_biomethane_nm3_per_year(
                _energy(injected_biomethane_gwh_pcs_per_year=10.0),
            )
        )

    def test_converts_gwh_pcs_to_nm3_per_year(self):
        # 100 GWh / (10 kWh/Nm3 * 1e-6) = 10_000_000 Nm3/an
        result = get_injected_biomethane_nm3_per_year(
            _energy(
                injected_biomethane_gwh_pcs_per_year=100.0,
                injected_biomethane_pcs_kwh_per_nm3=10.0,
            )
        )

        self.assertEqual(result, 10_000_000.0)

    def test_returns_zero_when_pcs_is_zero(self):
        result = get_injected_biomethane_nm3_per_year(
            _energy(
                injected_biomethane_gwh_pcs_per_year=100.0,
                injected_biomethane_pcs_kwh_per_nm3=0.0,
            )
        )

        self.assertEqual(result, 0.0)


class GetOperatingHoursTests(TestCase):
    def test_returns_none_when_energy_or_contract_is_missing(self):
        contract = BiomethaneContract(tariff_reference="2011", cmax=5.0)

        self.assertIsNone(get_operating_hours(None, contract, []))
        self.assertIsNone(get_operating_hours(_energy(), None, []))

    def test_tariff_rule_1_returns_none_without_monthly_injection_hours(self):
        contract = BiomethaneContract(
            tariff_reference="2011",
            cmax=5.0,
        )
        energy = _energy(
            injected_biomethane_gwh_pcs_per_year=1.0,
            injected_biomethane_pcs_kwh_per_nm3=10.0,
        )

        self.assertIsNone(get_operating_hours(energy, contract, []))
        self.assertIsNone(
            get_operating_hours(
                energy,
                contract,
                [
                    _monthly_report(
                        injected_volume_nm3=100.0,
                        average_monthly_flow_nm3_per_hour=0.0,
                    )
                ],
            )
        )

    def test_tariff_rule_1_sums_monthly_injection_hours(self):
        contract = BiomethaneContract(tariff_reference="2020", cmax=5.0)
        energy = _energy(
            injected_biomethane_gwh_pcs_per_year=0.01,
            injected_biomethane_pcs_kwh_per_nm3=10.0,
        )
        monthly_reports = [
            _monthly_report(month=1, injected_volume_nm3=100.0, average_monthly_flow_nm3_per_hour=10.0),
            _monthly_report(month=2, injected_volume_nm3=200.0, average_monthly_flow_nm3_per_hour=20.0),
        ]

        # Nm3/an = 0.01 / (10 * 1e-6) = 1000
        # totalInjectionHours = 10 + 10 = 20
        # 8760 * 1000 / (20 * 5) = 87600
        result = get_operating_hours(energy, contract, monthly_reports)

        self.assertEqual(result, 87600.0)

    def test_tariff_rule_1_rounds_to_integer(self):
        contract = BiomethaneContract(tariff_reference="2011", cmax=1.0)
        energy = _energy(
            injected_biomethane_gwh_pcs_per_year=0.001,
            injected_biomethane_pcs_kwh_per_nm3=10.0,
        )
        monthly_reports = [
            _monthly_report(month=1, injected_volume_nm3=33.0, average_monthly_flow_nm3_per_hour=11.0),
        ]

        # Nm3/an = 100, totalInjectionHours = 3
        # 8760 * 100 / (3 * 1) = 292000
        result = get_operating_hours(energy, contract, monthly_reports)

        self.assertEqual(result, 292000.0)

    def test_tariff_rule_2_uses_gwh_pcs_and_pap(self):
        contract = BiomethaneContract(tariff_reference="2021", pap_contracted=8.0)
        energy = _energy(injected_biomethane_gwh_pcs_per_year=8.0)

        # 8760 * 8 / 8 = 8760
        result = get_operating_hours(energy, contract, [])

        self.assertEqual(result, 8760.0)

    def test_tariff_rule_2_returns_none_when_pap_is_missing(self):
        contract = BiomethaneContract(tariff_reference="2023", pap_contracted=None)
        energy = _energy(injected_biomethane_gwh_pcs_per_year=8.0)

        self.assertIsNone(get_operating_hours(energy, contract, []))


class PreloadEnergyMetricsTests(TestCase):
    def setUp(self):
        self.producer = Entity.objects.create(name="Producer", entity_type=Entity.PRODUCER)
        self.buyer = Entity.objects.create(name="Buyer", entity_type=Entity.OPERATOR)
        self.year = 2024

        self.contract = BiomethaneContractFactory.create(
            producer=self.producer,
            buyer=self.buyer,
            tariff_reference="2011",
            cmax=5.0,
        )
        self.energy = BiomethaneEnergy.objects.create(
            producer=self.producer,
            year=self.year,
            injected_biomethane_gwh_pcs_per_year=0.01,
            injected_biomethane_pcs_kwh_per_nm3=10.0,
        )
        BiomethaneEnergyMonthlyReport.objects.create(
            energy=self.energy,
            month=1,
            injected_volume_nm3=100.0,
            average_monthly_flow_nm3_per_hour=10.0,
        )
        BiomethaneEnergyMonthlyReport.objects.create(
            energy=self.energy,
            month=2,
            injected_volume_nm3=200.0,
            average_monthly_flow_nm3_per_hour=20.0,
        )

    def test_preloads_both_computed_energy_fields(self):
        metrics = preload_energy_metrics(
            {self.producer.id: self.energy},
            {self.producer.id: self.contract},
        )[self.producer.id]

        self.assertEqual(metrics.injected_biomethane_nm3_per_year, 1000.0)
        self.assertEqual(metrics.operating_hours, 87600.0)

    def test_operating_hours_is_none_when_contract_is_missing(self):
        metrics = preload_energy_metrics(
            {self.producer.id: self.energy},
            {self.producer.id: None},
        )[self.producer.id]

        self.assertEqual(metrics.injected_biomethane_nm3_per_year, 1000.0)
        self.assertIsNone(metrics.operating_hours)

    def test_returns_empty_dict_when_no_energies(self):
        self.assertEqual(preload_energy_metrics({}, {}), {})
