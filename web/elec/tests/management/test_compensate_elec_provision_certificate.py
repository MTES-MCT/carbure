import json
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models import Entity
from core.tests_utils import assert_object_contains_data
from elec.models import ElecCertificateReadjustment, ElecProvisionCertificate
from entity.factories.entity import EntityFactory

COMPENSATION_YEAR = 2025


def run_command(enr_ratio, apply=False, log=False, year=COMPENSATION_YEAR):
    report = call_command(
        "compensate_elec_provision_certificate",
        enr_ratio=enr_ratio,
        year=year,
        apply=apply,
        log=log,
        stdout=StringIO(),
    )
    return json.loads(report)


class CompensateElecProvisionCertificateCommandTest(TestCase):
    def setUp(self):
        self.cpo1 = EntityFactory.create(entity_type=Entity.CPO)
        self.last_year = COMPENSATION_YEAR

    def create_certificate(
        self,
        *,
        source,
        energy_amount,
        enr_ratio=0.25,
        quarter=1,
        year=None,
        operating_unit="00001",
        cpo=None,
    ):
        return ElecProvisionCertificate.objects.create(
            cpo=cpo or self.cpo1,
            quarter=quarter,
            year=year or self.last_year,
            operating_unit=operating_unit,
            source=source,
            energy_amount=energy_amount,
            enr_ratio=enr_ratio,
        )

    def create_readjustment(self, *, energy_amount, enr_ratio=0.25, year=None, cpo=None):
        return ElecCertificateReadjustment.objects.create(
            cpo=cpo or self.cpo1,
            year=year or self.last_year,
            energy_amount=energy_amount,
            enr_ratio=enr_ratio,
            error_source=ElecCertificateReadjustment.MANUAL,
        )

    def test_returns_empty_list_when_no_eligible_certificates(self):
        result = run_command(enr_ratio=30)

        self.assertEqual(result, [])

    def test_returns_certificates_when_delta_positive_from_provision_certificates(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25)
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=2, energy_amount=1.5, enr_ratio=0.25)

        result = run_command(enr_ratio=30)

        # One compensation certificate per year when delta is positive
        self.assertEqual(len(result), 1)

        # Energy amount in certificate is already renewable energy.
        # So we first recompute total energy with old ratio, then re-apply new ratio:
        # quarter 1: (1.0 / 0.25) * 0.30 - 1.0 = 0.20 MWh
        # quarter 2: (1.5 / 0.25) * 0.30 - 1.5 = 0.30 MWh
        expected_data = [
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "ALL",
                "energy_amount": 0.5,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        ]
        for i, cert in enumerate(result):
            assert_object_contains_data(
                self,
                cert,
                expected_data[i],
            )

    def test_returns_no_certificate_when_delta_zero(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=2.0, enr_ratio=0.25)
        self.create_certificate(source=ElecProvisionCertificate.QUALICHARGE, quarter=2, energy_amount=3.0, enr_ratio=0.25)

        result = run_command(enr_ratio=25)

        self.assertEqual(result, [])

    def test_excludes_compensation_sources_from_base_calculation(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25)
        self.create_certificate(
            source=ElecProvisionCertificate.ADMIN_ERROR_COMPENSATION,
            quarter=1,
            energy_amount=10.0,
            enr_ratio=0.25,
        )

        result = run_command(enr_ratio=30)

        # Only MANUAL contributes to base computation: expected delta = 1.0 * (0.30 / 0.25 - 1) = 0.2
        self.assertEqual(len(result), 1)

        assert_object_contains_data(
            self,
            result[0],
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "ALL",
                "energy_amount": 0.2,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        )

    def test_excludes_enr_ratio_compensation_source_from_base_calculation(self):
        self.create_certificate(
            source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            quarter=1,
            energy_amount=1.0,
            enr_ratio=0.25,
        )

        result = run_command(enr_ratio=30)

        self.assertEqual(result, [])

    def test_includes_meter_readings_source_in_base_calculation(self):
        self.create_certificate(source=ElecProvisionCertificate.METER_READINGS, quarter=1, energy_amount=1.0, enr_ratio=0.25)

        result = run_command(enr_ratio=30)

        self.assertEqual(len(result), 1)
        assert_object_contains_data(
            self,
            result[0],
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "ALL",
                "energy_amount": 0.2,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        )

    def test_returns_no_certificate_when_certificate_already_created(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25)

        # Create compensation certificate for this key
        result = run_command(enr_ratio=30, apply=True)

        self.assertEqual(len(result), 1)

        # Should return no certificates because compensation is already created for this key.
        new_result = run_command(enr_ratio=35, apply=True)

        self.assertEqual(new_result, [])

    def test_existing_compensation_on_another_year_does_not_block_current_year(self):
        self.create_certificate(
            source=ElecProvisionCertificate.MANUAL,
            quarter=1,
            year=COMPENSATION_YEAR,
            energy_amount=1.0,
            enr_ratio=0.25,
        )
        self.create_certificate(
            source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            quarter=1,
            year=2024,
            energy_amount=0.5,
            enr_ratio=0.30,
        )

        result = run_command(enr_ratio=30, year=COMPENSATION_YEAR)

        self.assertEqual(len(result), 1)
        assert_object_contains_data(
            self,
            result[0],
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": COMPENSATION_YEAR,
                "operating_unit": "ALL",
                "energy_amount": 0.2,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        )

    def test_ignores_readjustment_from_other_year(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25)
        self.create_readjustment(energy_amount=0.5, year=2024)

        result = run_command(enr_ratio=30)

        self.assertEqual(len(result), 1)
        assert_object_contains_data(
            self,
            result[0],
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "ALL",
                "energy_amount": 0.2,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        )

    def test_calculates_compensation_independently_for_each_cpo(self):
        cpo2 = EntityFactory.create(entity_type=Entity.CPO)
        self.create_certificate(
            source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25, cpo=self.cpo1
        )
        self.create_certificate(
            source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=2.0, enr_ratio=0.25, cpo=cpo2
        )

        result = run_command(enr_ratio=30)

        self.assertEqual(len(result), 2)
        amounts_by_cpo = {certificate["cpo_id"]: certificate["energy_amount"] for certificate in result}
        self.assertEqual(amounts_by_cpo[self.cpo1.id], 0.2)
        self.assertEqual(amounts_by_cpo[cpo2.id], 0.4)

    def test_computes_delta_per_certificate_when_enr_ratio_differs_for_same_cpo(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=100.0, enr_ratio=0.25)
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=2, energy_amount=200.0, enr_ratio=0.28)

        result = run_command(enr_ratio=30)

        self.assertEqual(len(result), 1)
        # Expected formula:
        # cert1 delta = (100 / 0.25) * 0.30 - 100 = 20.00
        # cert2 delta = (200 / 0.28) * 0.30 - 200 = 14.29 (rounded)
        # total delta = 34.29
        assert_object_contains_data(
            self,
            result[0],
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "ALL",
                "energy_amount": 34.29,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        )

    def test_computes_delta_with_mixed_enr_ratio_and_readjustment_amount(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=100.0, enr_ratio=0.25)
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=2, energy_amount=200.0, enr_ratio=0.28)
        self.create_readjustment(
            energy_amount=50.0,
            enr_ratio=0.25,  # non-renewable base = 50 / 0.25 = 200 MWh
            year=COMPENSATION_YEAR,
        )

        result = run_command(enr_ratio=30)

        self.assertEqual(len(result), 1)
        # delta certificats = (100 / 0.25 + 200 / 0.28) * 0.30 - (100 + 200) = 34.29
        # delta réajustements = (50 / 0.25) * 0.30 - 50 = 10.00
        # compensation nette = 34.29 - 10.00 = 24.29
        assert_object_contains_data(
            self,
            result[0],
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "ALL",
                "energy_amount": 24.29,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        )

    def test_computes_compensation_with_real_world_volumes_and_readjustments(self):
        """
        Cas réel : certificats renouvelables + réajustements, passage de 25 % à 30,81 %.

        Entrées :
        - certificats renouvelables : 2 931 MWh (enr_ratio = 0,25)
        - réajustements renouvelables : 532,51 MWh (enr_ratio = 0,25)
        - nouveau ratio : 0,3081 (30,81 %)

        Calcul attendu (par bloc, puis net) :
        - non renouvelable certificats = 2 931 / 0,25 = 11 724,00 MWh
        - non renouvelable réajustements = 532,51 / 0,25 = 2 130,04 MWh
        - delta certificats = 11 724,00 * 0,3081 - 2 931,00 = 681,16 MWh
        - delta réajustements = 2 130,04 * 0,3081 - 532,51 = 123,76 MWh
        - compensation nette = 681,16 - 123,76 = 557,41 MWh (arrondi final sur le net)
        """
        renewable_certificates_mwh = 2931.0
        renewable_readjustments_mwh = 532.51
        old_enr_ratio = 0.25
        new_enr_ratio = 0.3081

        non_renewable_certificates_mwh = renewable_certificates_mwh / old_enr_ratio
        non_renewable_readjustments_mwh = renewable_readjustments_mwh / old_enr_ratio

        certificates_delta_mwh = non_renewable_certificates_mwh * new_enr_ratio - renewable_certificates_mwh
        readjustments_delta_mwh = non_renewable_readjustments_mwh * new_enr_ratio - renewable_readjustments_mwh
        expected_compensation_mwh = round(certificates_delta_mwh - readjustments_delta_mwh, 2)

        self.create_certificate(
            source=ElecProvisionCertificate.MANUAL,
            quarter=1,
            energy_amount=renewable_certificates_mwh,
            enr_ratio=old_enr_ratio,
        )
        self.create_readjustment(
            energy_amount=renewable_readjustments_mwh,
            enr_ratio=old_enr_ratio,
            year=COMPENSATION_YEAR,
        )

        result = run_command(enr_ratio=new_enr_ratio * 100)

        self.assertEqual(len(result), 1)
        assert_object_contains_data(
            self,
            result[0],
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": COMPENSATION_YEAR,
                "operating_unit": "ALL",
                "energy_amount": expected_compensation_mwh,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        )
