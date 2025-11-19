import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.factories.provision_certificate_qualicharge import ElecProvisionCertificateQualichargeFactory
from entity.factories import EntityFactory


class ElecProvisionCertificateQualichargeViewSetListTest(TestCase):
    """Tests for certificate listing and retrieval"""

    def setUp(self):
        self.cpo = EntityFactory.create(
            name="Test CPO",
            entity_type=Entity.CPO,
            has_elec=True,
            registration_id="123456789",
        )
        self.other_cpo = EntityFactory.create(
            name="Other CPO",
            entity_type=Entity.CPO,
            has_elec=True,
            registration_id="987654321",
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.cpo, "RW")],
        )

        # Create certificates for the user's CPO
        for i in range(5):
            ElecProvisionCertificateQualichargeFactory(
                cpo=self.cpo,
                date_from=datetime.date(2023, 1, 1),
                date_to=datetime.date(2023, 3, 31),
                year=2023,
                operating_unit=f"FR00{i}",
                station_id=f"FRXYZP11111{i}",
                energy_amount=1000.0 * (i + 1),
                cpo_validated=True,
            )

        # Create certificate for another CPO (should not appear)
        ElecProvisionCertificateQualichargeFactory(
            cpo=self.other_cpo,
            operating_unit="FR999",
            station_id="FRXYZP999999",
            energy_amount=9999.0,
            cpo_validated=True,
        )

        self.list_params = {
            "path": reverse("elec-provision-certificate-qualicharge-list"),
            "query_params": {"entity_id": self.cpo.id},
        }

    def test_list_only_own_certificates(self):
        """Test that user only sees their own certificates"""
        response = self.client.get(**self.list_params)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 5)
        self.assertEqual(len(data["results"]), 5)

        # Verify that only the CPO's certificates are returned
        for cert in data["results"]:
            self.assertEqual(cert["cpo"]["id"], self.cpo.id)

        # Verify that no certificates from other_cpo are present
        for cert in data["results"]:
            self.assertNotEqual(cert["station_id"], "FRXYZP999999")

    def test_list_with_filter_year(self):
        """Test filtering by year"""
        # Create a certificate for another year
        ElecProvisionCertificateQualichargeFactory(
            cpo=self.cpo,
            date_from=datetime.date(2024, 1, 1),
            date_to=datetime.date(2024, 3, 31),
            year=2024,
            operating_unit="FR099",
            station_id="FRXYZP888888",
            energy_amount=8888.0,
            cpo_validated=True,
        )

        self.list_params["query_params"]["year"] = 2024
        response = self.client.get(**self.list_params)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["year"], 2024)

    def test_list_metadata(self):
        """Test pagination metadata (total_quantity)"""
        response = self.client.get(**self.list_params)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify that total_quantity is present and correct
        # Sum = 1000 + 2000 + 3000 + 4000 + 5000 = 15000
        self.assertIn("total_quantity", data)
        self.assertEqual(data["total_quantity"], 15000.0)

    def test_retrieve_certificate(self):
        """Test certificate retrieval"""
        certificate = ElecProvisionCertificateQualichargeFactory(
            cpo=self.cpo,
            date_from=datetime.date(2023, 1, 1),
            date_to=datetime.date(2023, 3, 31),
            year=2023,
            operating_unit="FR001",
            station_id="FRXYZP123456",
            energy_amount=1000.0,
            cpo_validated=True,
        )

        response = self.client.get(
            reverse("elec-provision-certificate-qualicharge-detail", kwargs={"pk": certificate.id}),
            {"entity_id": self.cpo.id},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], certificate.id)
        self.assertEqual(data["station_id"], "FRXYZP123456")
        self.assertEqual(data["energy_amount"], 1000.0)

    def test_retrieve_non_existing_certificate(self):
        """Test retrieval of non-existing certificate"""
        response = self.client.get(
            reverse("elec-provision-certificate-qualicharge-detail", kwargs={"pk": 99999}),
            {"entity_id": self.cpo.id},
        )

        self.assertEqual(response.status_code, 404)


class ElecProvisionCertificateQualichargeViewSetAdminTest(TestCase):
    """Tests for ELEC administrators"""

    def setUp(self):
        from core.models import ExternalAdminRights

        self.admin_entity = EntityFactory.create(
            name="Admin DGEC",
            entity_type=Entity.EXTERNAL_ADMIN,
        )
        # Add ELEC external admin rights to the entity
        ExternalAdminRights.objects.create(entity=self.admin_entity, right=ExternalAdminRights.ELEC)

        self.cpo = EntityFactory.create(
            name="Test CPO",
            entity_type=Entity.CPO,
            registration_id="123456789",
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.admin_entity, "ADMIN")],
        )

        # Create certificates for different CPOs using factory
        for i in range(3):
            ElecProvisionCertificateQualichargeFactory(
                cpo=self.cpo,
                date_from=datetime.date(2023, 1, 1),
                date_to=datetime.date(2023, 3, 31),
                year=2023,
                operating_unit=f"FR00{i}",
                station_id=f"FRXYZP11111{i}",
                energy_amount=1000.0,
                cpo_validated=True,
            )

    def test_admin_can_see_all_certificates(self):
        """Test that admin can see all certificates"""
        response = self.client.get(
            reverse("elec-provision-certificate-qualicharge-list"),
            {"entity_id": self.admin_entity.id},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 3)
