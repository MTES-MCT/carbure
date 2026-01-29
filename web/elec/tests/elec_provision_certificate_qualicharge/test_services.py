import datetime

from django.test import TestCase

from core.models import Entity
from elec.factories.provision_certificate_qualicharge import ElecProvisionCertificateQualichargeFactory
from elec.models import ElecProvisionCertificate, ElecProvisionCertificateQualicharge
from elec.services.qualicharge import (
    _prepare_certificates_bulk,
    create_provision_certificates_from_qualicharge,
    process_certificates_batch,
    resolve_cpo,
)


class ResolveCpoTest(TestCase):
    """Tests for the resolve_cpo function"""

    @classmethod
    def setUpTestData(cls):
        """Create test entities (not modified during tests)"""
        cls.cpo_single = Entity.objects.create(
            name="Test CPO",
            entity_type=Entity.CPO,
            registration_id="111111111",
        )

        # Multiple entities with same SIREN - with master
        Entity.objects.create(
            name="CPO 1",
            entity_type=Entity.CPO,
            registration_id="222222222",
            is_master=False,
        )
        cls.master_cpo = Entity.objects.create(
            name="CPO Master",
            entity_type=Entity.CPO,
            registration_id="222222222",
            is_master=True,
        )

        # Multiple entities with same SIREN - without master
        Entity.objects.create(
            name="CPO A",
            entity_type=Entity.CPO,
            registration_id="333333333",
            is_master=False,
        )
        Entity.objects.create(
            name="CPO B",
            entity_type=Entity.CPO,
            registration_id="333333333",
            is_master=False,
        )

    def test_resolve_existing_entity(self):
        """Test resolving an existing entity"""
        result_cpo, unknown_siren = resolve_cpo("111111111")
        self.assertEqual(result_cpo, self.cpo_single)
        self.assertIsNone(unknown_siren)

    def test_resolve_non_existing_entity(self):
        """Test resolving a non-existing entity"""
        result_cpo, unknown_siren = resolve_cpo("999999999")
        self.assertIsNone(result_cpo)
        self.assertEqual(unknown_siren, "999999999")

    def test_resolve_multiple_entities_with_master(self):
        """Test resolving with multiple entities, including a master"""
        result_cpo, unknown_siren = resolve_cpo("222222222")
        self.assertEqual(result_cpo, self.master_cpo)
        self.assertIsNone(unknown_siren)

    def test_resolve_multiple_entities_without_master(self):
        """Test resolving with multiple entities without a master"""
        result_cpo, unknown_siren = resolve_cpo("333333333")
        self.assertIsNone(result_cpo)
        self.assertEqual(unknown_siren, "333333333")


class ProcessCertificatesBatchTest(TestCase):
    """Tests for the process_certificates_batch function - orchestration only"""

    def setUp(self):
        self.cpo = Entity.objects.create(
            name="Test CPO",
            entity_type=Entity.CPO,
            registration_id="123456789",
        )

        self.validated_data = [
            {
                "siren": "123456789",
                "operational_units": [
                    {
                        "code": "FR001",
                        "from": datetime.date(2023, 1, 1),
                        "to": datetime.date(2023, 3, 31),
                        "stations": [
                            {
                                "id": "FRXYZP123456",
                                "energy": 1000.0,
                                "is_controlled": True,
                            }
                        ],
                    }
                ],
            }
        ]
        self.double_validated = set()

    def test_process_valid_batch(self):
        """Test orchestration with valid data"""
        errors = process_certificates_batch(self.validated_data, self.double_validated)

        self.assertEqual(len(errors), 0)
        self.assertEqual(ElecProvisionCertificateQualicharge.objects.count(), 1)

    def test_process_multiple_items(self):
        """Test orchestration with multiple items in batch"""
        self.validated_data.append(
            {
                "siren": "999999999",
                "operational_units": [
                    {
                        "code": "FR002",
                        "from": datetime.date(2023, 1, 1),
                        "to": datetime.date(2023, 3, 31),
                        "stations": [
                            {
                                "id": "FRXYZP999999",
                                "energy": 500.0,
                                "is_controlled": False,
                            }
                        ],
                    }
                ],
            }
        )

        errors = process_certificates_batch(self.validated_data, self.double_validated)

        self.assertEqual(len(errors), 0)
        # Should create certificates for both items
        self.assertEqual(ElecProvisionCertificateQualicharge.objects.count(), 2)


class PrepareCertificatesBulkTest(TestCase):
    """Tests for the _prepare_certificates_bulk function"""

    def setUp(self):
        self.cpo = Entity.objects.create(
            name="Test CPO",
            entity_type=Entity.CPO,
            registration_id="123456789",
        )

        self.unit_data = {
            "code": "FR001",
            "from": datetime.date(2023, 1, 1),
            "to": datetime.date(2023, 3, 31),
            "stations": [
                {
                    "id": "FRXYZP123456",
                    "energy": 1000.0,
                    "is_controlled": True,
                }
            ],
        }
        self.double_validated = set()
        self.existing_certs = {}
        self.to_create = []
        self.to_update = []

    def test_create_certificate_with_cpo(self):
        """Test creating certificate with a valid CPO"""
        errors = _prepare_certificates_bulk(
            self.unit_data, self.cpo, None, self.double_validated, self.existing_certs, self.to_create, self.to_update
        )

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(self.to_create), 1)
        self.assertEqual(len(self.to_update), 0)
        cert = self.to_create[0]
        self.assertEqual(cert.cpo, self.cpo)
        self.assertEqual(cert.station_id, "FRXYZP123456")
        self.assertEqual(cert.energy_amount, 1000.0)
        self.assertEqual(cert.operating_unit, "FR001")

    def test_create_certificate_with_unknown_siren(self):
        """Test creating certificate with unknown SIREN"""
        errors = _prepare_certificates_bulk(
            self.unit_data, None, "999999999", self.double_validated, self.existing_certs, self.to_create, self.to_update
        )

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(self.to_create), 1)
        cert = self.to_create[0]
        self.assertIsNone(cert.cpo)
        self.assertEqual(cert.unknown_siren, "999999999")

    def test_reject_double_validated_certificate(self):
        """Test rejecting already double-validated certificates"""
        self.double_validated = {("FRXYZP123456", datetime.date(2023, 1, 1), datetime.date(2023, 3, 31))}

        errors = _prepare_certificates_bulk(
            self.unit_data, self.cpo, None, self.double_validated, self.existing_certs, self.to_create, self.to_update
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("already validated", errors[0]["error"])
        self.assertEqual(len(self.to_create), 0)
        self.assertEqual(len(self.to_update), 0)

    def test_process_multiple_stations(self):
        """Test processing multiple stations in one operational unit"""
        self.unit_data["stations"].append(
            {
                "id": "FRXYZP222222",
                "energy": 2000.0,
                "is_controlled": False,
            }
        )

        errors = _prepare_certificates_bulk(
            self.unit_data, self.cpo, None, self.double_validated, self.existing_certs, self.to_create, self.to_update
        )

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(self.to_create), 2)

    def test_update_existing_certificate(self):
        """Test updating an existing certificate"""
        existing_cert = ElecProvisionCertificateQualicharge.objects.create(
            cpo=self.cpo,
            station_id="FRXYZP123456",
            date_from=datetime.date(2023, 1, 1),
            date_to=datetime.date(2023, 3, 31),
            year=2023,
            operating_unit="FR001",
            energy_amount=500.0,
            is_controlled_by_qualicharge=False,
        )

        # Add to existing_certs dict
        key = ("FRXYZP123456", datetime.date(2023, 1, 1), datetime.date(2023, 3, 31))
        self.existing_certs[key] = existing_cert

        errors = _prepare_certificates_bulk(
            self.unit_data, self.cpo, None, self.double_validated, self.existing_certs, self.to_create, self.to_update
        )

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(self.to_create), 0)
        self.assertEqual(len(self.to_update), 1)
        cert = self.to_update[0]
        self.assertEqual(cert.energy_amount, 1000.0)  # Updated
        self.assertTrue(cert.is_controlled_by_qualicharge)  # Updated


class CreateProvisionCertificatesFromQualichargeTest(TestCase):
    """Tests for the create_provision_certificates_from_qualicharge function"""

    def setUp(self):
        self.cpo = Entity.objects.create(
            name="Test CPO",
            entity_type=Entity.CPO,
            registration_id="123456789",
        )

    def test_create_provision_certificates_with_aggregation(self):
        """Test that certificates are grouped and energy amounts are summed"""
        # Create two double-validated certificates with same CPO, unit, and period
        ElecProvisionCertificateQualichargeFactory(
            double_validated=True,
            cpo=self.cpo,
            operating_unit="FR001",
            date_from=datetime.date(2023, 1, 1),
            date_to=datetime.date(2023, 3, 31),
            year=2023,
            energy_amount=1000.0,
        )
        ElecProvisionCertificateQualichargeFactory(
            double_validated=True,
            cpo=self.cpo,
            operating_unit="FR001",
            date_from=datetime.date(2023, 1, 1),
            date_to=datetime.date(2023, 3, 31),
            year=2023,
            energy_amount=2000.0,
        )

        queryset = ElecProvisionCertificateQualicharge.objects.all()
        create_provision_certificates_from_qualicharge(queryset)

        # Should create one aggregated provision certificate
        self.assertEqual(ElecProvisionCertificate.objects.count(), 1)
        cert = ElecProvisionCertificate.objects.first()
        self.assertEqual(cert.cpo, self.cpo)
        self.assertEqual(cert.operating_unit, "FR001")
        self.assertEqual(cert.energy_amount, 3000.0)
        self.assertEqual(cert.remaining_energy_amount, 3000.0)
        self.assertEqual(cert.quarter, 1)
        self.assertEqual(cert.year, 2023)
        self.assertEqual(cert.source, ElecProvisionCertificate.QUALICHARGE)

    def test_create_multiple_groups(self):
        """Test that different groups create separate provision certificates"""
        ElecProvisionCertificateQualichargeFactory(
            double_validated=True,
            cpo=self.cpo,
            operating_unit="FR001",
            date_from=datetime.date(2023, 1, 1),
            date_to=datetime.date(2023, 3, 31),
            year=2023,
            energy_amount=1000.0,
        )
        ElecProvisionCertificateQualichargeFactory(
            double_validated=True,
            cpo=self.cpo,
            operating_unit="FR002",  # Different unit
            date_from=datetime.date(2023, 1, 1),
            date_to=datetime.date(2023, 3, 31),
            year=2023,
            energy_amount=2000.0,
        )

        queryset = ElecProvisionCertificateQualicharge.objects.all()
        create_provision_certificates_from_qualicharge(queryset)

        # Should create two separate provision certificates
        self.assertEqual(ElecProvisionCertificate.objects.count(), 2)

    def test_filter_only_both_validated(self):
        """Test that only BOTH validated certificates are processed"""
        ElecProvisionCertificateQualichargeFactory(
            cpo_validated=True,
            cpo=self.cpo,
            operating_unit="FR001",
            date_from=datetime.date(2023, 1, 1),
            date_to=datetime.date(2023, 3, 31),
            year=2023,
            energy_amount=1000.0,
        )
        ElecProvisionCertificateQualichargeFactory(
            double_validated=True,
            cpo=self.cpo,
            operating_unit="FR001",
            date_from=datetime.date(2023, 1, 1),
            date_to=datetime.date(2023, 3, 31),
            year=2023,
            energy_amount=2000.0,
        )

        queryset = ElecProvisionCertificateQualicharge.objects.all()
        create_provision_certificates_from_qualicharge(queryset)

        # Should create only one certificate with energy from the BOTH validated one
        self.assertEqual(ElecProvisionCertificate.objects.count(), 1)
        cert = ElecProvisionCertificate.objects.first()
        self.assertEqual(cert.energy_amount, 2000.0)

    def test_calculate_quarter_from_date(self):
        """Test that quarter is correctly calculated from date_from"""
        test_cases = [
            (datetime.date(2023, 1, 15), 1),
            (datetime.date(2023, 4, 15), 2),
            (datetime.date(2023, 7, 15), 3),
            (datetime.date(2023, 10, 15), 4),
        ]

        for date_from, expected_quarter in test_cases:
            with self.subTest(date=date_from):
                ElecProvisionCertificateQualicharge.objects.all().delete()
                ElecProvisionCertificate.objects.all().delete()

                ElecProvisionCertificateQualichargeFactory(
                    double_validated=True,
                    cpo=self.cpo,
                    operating_unit="FR001",
                    date_from=date_from,
                    date_to=date_from,
                    year=2023,
                    energy_amount=1000.0,
                )

                queryset = ElecProvisionCertificateQualicharge.objects.all()
                create_provision_certificates_from_qualicharge(queryset)

                cert = ElecProvisionCertificate.objects.first()
                self.assertEqual(cert.quarter, expected_quarter)
