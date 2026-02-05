import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.factories.provision_certificate_qualicharge import ElecProvisionCertificateQualichargeFactory
from elec.models import ElecProvisionCertificateQualicharge
from entity.factories import EntityFactory


class FilterActionMixinTest(TestCase):
    """Tests for the filter action mixin"""

    def setUp(self):
        self.cpo1 = EntityFactory.create(
            name="CPO Alpha",
            entity_type=Entity.CPO,
            has_elec=True,
            registration_id="111111111",
        )
        self.cpo2 = EntityFactory.create(
            name="CPO Beta",
            entity_type=Entity.CPO,
            has_elec=True,
            registration_id="222222222",
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.cpo1, "RW")],
        )

        # Create certificates with different attributes
        ElecProvisionCertificateQualichargeFactory(
            cpo=self.cpo1,
            year=2023,
            operating_unit="FR001",
            station_id="FRXYZP111111",
            validated_by=ElecProvisionCertificateQualicharge.CPO,
            date_from=datetime.date(2023, 1, 1),
        )
        ElecProvisionCertificateQualichargeFactory(
            cpo=self.cpo1,
            year=2023,
            operating_unit="FR002",
            station_id="FRXYZP222222",
            validated_by=ElecProvisionCertificateQualicharge.DGEC,
            date_from=datetime.date(2023, 4, 1),
        )
        ElecProvisionCertificateQualichargeFactory(
            cpo=self.cpo1,
            year=2024,
            operating_unit="FR003",
            station_id="FRXYZP333333",
            validated_by=ElecProvisionCertificateQualicharge.BOTH,
            date_from=datetime.date(2024, 1, 1),
        )
        # Certificate for another CPO (should not appear for cpo1 user)
        ElecProvisionCertificateQualichargeFactory(
            cpo=self.cpo2,
            year=2023,
            operating_unit="FR999",
            station_id="FRXYZP999999",
            validated_by=ElecProvisionCertificateQualicharge.CPO,
        )

        self.url = reverse("elec-provision-certificate-qualicharge-filters")

    def test_filter_year(self):
        """Test filtering years"""
        response = self.client.get(
            self.url,
            {
                "entity_id": self.cpo1.id,
                "filter": "year",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(2023, data)
        self.assertIn(2024, data)
        self.assertEqual(len(data), 2)

    def test_filter_validated_by(self):
        """Test filtering validation statuses"""
        response = self.client.get(
            self.url,
            {
                "entity_id": self.cpo1.id,
                "filter": "validated_by",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(ElecProvisionCertificateQualicharge.CPO, data)
        self.assertIn(ElecProvisionCertificateQualicharge.DGEC, data)
        self.assertIn(ElecProvisionCertificateQualicharge.BOTH, data)

    def test_filter_operating_unit(self):
        """Test filtering operating units"""
        response = self.client.get(
            self.url,
            {
                "entity_id": self.cpo1.id,
                "filter": "operating_unit",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("FR001", data)
        self.assertIn("FR002", data)
        self.assertIn("FR003", data)
        # Should not include FR999 from other CPO
        self.assertNotIn("FR999", data)

    def test_filter_station_id(self):
        """Test filtering station IDs"""
        response = self.client.get(
            self.url,
            {
                "entity_id": self.cpo1.id,
                "filter": "station_id",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("FRXYZP111111", data)
        self.assertIn("FRXYZP222222", data)
        self.assertIn("FRXYZP333333", data)
        # Should not include station from other CPO
        self.assertNotIn("FRXYZP999999", data)

    def test_filter_date_from(self):
        """Test filtering date_from values"""
        response = self.client.get(
            self.url,
            {
                "entity_id": self.cpo1.id,
                "filter": "date_from",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # dates are returned as strings
        self.assertIn("2023-01-01", data)
        self.assertIn("2023-04-01", data)
        self.assertIn("2024-01-01", data)

    def test_filter_cpo(self):
        """Test filtering CPO names"""
        response = self.client.get(
            self.url,
            {
                "entity_id": self.cpo1.id,
                "filter": "cpo",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should only see own CPO name
        self.assertIn("CPO Alpha", data)
        self.assertNotIn("CPO Beta", data)

    def test_filter_with_additional_filters(self):
        """Test that other filters are applied when retrieving filter values"""
        response = self.client.get(
            self.url,
            {
                "entity_id": self.cpo1.id,
                "filter": "operating_unit",
                "year": 2023,  # Additional filter
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Only operating units from 2023
        self.assertIn("FR001", data)
        self.assertIn("FR002", data)
        self.assertNotIn("FR003", data)  # This is from 2024

    def test_filter_invalid_filter_name(self):
        """Test with an invalid filter name"""
        with self.assertRaises(Exception) as context:
            self.client.get(
                self.url,
                {
                    "entity_id": self.cpo1.id,
                    "filter": "invalid_filter",
                },
            )

        self.assertIn("does not exist", str(context.exception))

    def test_filter_missing_filter_param(self):
        """Test without filter parameter"""
        with self.assertRaises(Exception) as context:
            self.client.get(
                self.url,
                {
                    "entity_id": self.cpo1.id,
                },
            )

        self.assertIn("No filter was specified", str(context.exception))


class FilterActionMixinAdminTest(TestCase):
    """Tests for filter action with admin rights"""

    def setUp(self):
        from core.models import ExternalAdminRights

        self.admin_entity = EntityFactory.create(
            name="Admin DGEC",
            entity_type=Entity.EXTERNAL_ADMIN,
        )
        ExternalAdminRights.objects.create(entity=self.admin_entity, right=ExternalAdminRights.ELEC)

        self.cpo1 = EntityFactory.create(
            name="CPO Alpha",
            entity_type=Entity.CPO,
            registration_id="111111111",
        )
        self.cpo2 = EntityFactory.create(
            name="CPO Beta",
            entity_type=Entity.CPO,
            registration_id="222222222",
        )

        self.user = setup_current_user(
            self,
            "admin@carbure.local",
            "Admin",
            "adminpwd",
            [(self.admin_entity, "ADMIN")],
        )

        # Create certificates for different CPOs
        ElecProvisionCertificateQualichargeFactory(
            cpo=self.cpo1,
            operating_unit="FR001",
        )
        ElecProvisionCertificateQualichargeFactory(
            cpo=self.cpo2,
            operating_unit="FR002",
        )

        self.url = reverse("elec-provision-certificate-qualicharge-filters")

    def test_admin_can_filter_all_cpos(self):
        """Test that admin can see all CPO names"""
        response = self.client.get(
            self.url,
            {
                "entity_id": self.admin_entity.id,
                "filter": "cpo",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Admin should see all CPOs
        self.assertIn("CPO Alpha", data)
        self.assertIn("CPO Beta", data)
