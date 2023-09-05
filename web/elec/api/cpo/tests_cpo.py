import datetime
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse

from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


class ElecCPOTest(TestCase):
    def setUp(self):
        self.cpo = Entity.objects.create(
            name="CPO",
            entity_type=Entity.CPO,
            has_elec=True,
        )

        self.operator = Entity.objects.create(
            name="OPERATOR",
            entity_type=Entity.OPERATOR,
            has_elec=True,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.cpo, "RW")],
        )

        self.prov1 = ElecProvisionCertificate.objects.create(
            cpo=self.cpo,
            quarter=4,
            year=2022,
            operating_unit="XYZ",
            energy_amount=4000,
            remaining_energy_amount=0,
        )
        self.prov2 = ElecProvisionCertificate.objects.create(
            cpo=self.cpo,
            quarter=1,
            year=2023,
            operating_unit="ABCD",
            energy_amount=1000,
            remaining_energy_amount=500,
        )
        self.prov3 = ElecProvisionCertificate.objects.create(
            cpo=self.cpo,
            quarter=2,
            year=2023,
            operating_unit="DCBA",
            energy_amount=2000,
            remaining_energy_amount=2000,
        )

    def test_transfer_provision_certificate_pile_poil(self):
        self.client.post(
            reverse("elec-cpo-transfer-provision-certificate"),
            {
                "entity_id": self.cpo.id,
                "energy_mwh": 500,
                "client_id": self.operator.id,
            },
        )

        prov1 = ElecProvisionCertificate.objects.get(pk=self.prov1.id)
        prov2 = ElecProvisionCertificate.objects.get(pk=self.prov2.id)
        prov3 = ElecProvisionCertificate.objects.get(pk=self.prov3.id)

        self.assertEqual(prov1.remaining_energy_amount, 0)
        self.assertEqual(prov2.remaining_energy_amount, 0)
        self.assertEqual(prov3.remaining_energy_amount, 2000)

        transfer_cert = ElecTransferCertificate.objects.all().first()
        self.assertEqual(transfer_cert.energy_amount, 500)
        self.assertEqual(transfer_cert.supplier_id, self.cpo.id)
        self.assertEqual(transfer_cert.client_id, self.operator.id)

    def test_transfer_provision_certificate_multiple(self):
        self.client.post(
            reverse("elec-cpo-transfer-provision-certificate"),
            {
                "entity_id": self.cpo.id,
                "energy_mwh": 1500,
                "client_id": self.operator.id,
            },
        )

        prov1 = ElecProvisionCertificate.objects.get(pk=self.prov1.id)
        prov2 = ElecProvisionCertificate.objects.get(pk=self.prov2.id)
        prov3 = ElecProvisionCertificate.objects.get(pk=self.prov3.id)

        self.assertEqual(prov1.remaining_energy_amount, 0)
        self.assertEqual(prov2.remaining_energy_amount, 0)
        self.assertEqual(prov3.remaining_energy_amount, 1000)

        transfer_cert = ElecTransferCertificate.objects.all().first()
        self.assertEqual(transfer_cert.energy_amount, 1500)
        self.assertEqual(transfer_cert.supplier_id, self.cpo.id)
        self.assertEqual(transfer_cert.client_id, self.operator.id)

    def test_transfer_provision_certificate_too_much(self):
        response = self.client.post(
            reverse("elec-cpo-transfer-provision-certificate"),
            {
                "entity_id": self.cpo.id,
                "energy_mwh": 10000,
                "client_id": self.operator.id,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "NOT_ENOUGH_ENERGY")

        prov1 = ElecProvisionCertificate.objects.get(pk=self.prov1.id)
        prov2 = ElecProvisionCertificate.objects.get(pk=self.prov2.id)
        prov3 = ElecProvisionCertificate.objects.get(pk=self.prov3.id)

        self.assertEqual(prov1.remaining_energy_amount, 0)
        self.assertEqual(prov2.remaining_energy_amount, 500)
        self.assertEqual(prov3.remaining_energy_amount, 2000)

        transfer_cert_count = ElecTransferCertificate.objects.count()
        self.assertEqual(transfer_cert_count, 0)

    def test_cancel_transfer_certificate(self):
        self.client.post(
            reverse("elec-cpo-transfer-provision-certificate"),
            {
                "entity_id": self.cpo.id,
                "energy_mwh": 1500,
                "client_id": self.operator.id,
            },
        )

        transfer = ElecTransferCertificate.objects.last()
        self.assertEqual(transfer.energy_amount, 1500)

        response = self.client.post(
            reverse("elec-cpo-cancel-transfer-certificate"),
            {
                "entity_id": self.cpo.id,
                "transfer_certificate_id": transfer.id,
            },
        )

        self.assertEqual(response.status_code, 200)

        prov1 = ElecProvisionCertificate.objects.get(pk=self.prov1.id)
        prov2 = ElecProvisionCertificate.objects.get(pk=self.prov2.id)
        prov3 = ElecProvisionCertificate.objects.get(pk=self.prov3.id)

        self.assertEqual(prov1.remaining_energy_amount, 0)
        self.assertEqual(prov2.remaining_energy_amount, 500)
        self.assertEqual(prov3.remaining_energy_amount, 2000)
