import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
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
            reverse("elec-cpo-create-transfer-certificate"),
            {
                "entity_id": self.cpo.id,
                "energy_mwh": 500,
                "client_id": self.operator.id,
            },
        )

        prov1 = ElecProvisionCertificate.objects.get(pk=self.prov1.id)
        prov2 = ElecProvisionCertificate.objects.get(pk=self.prov2.id)
        prov3 = ElecProvisionCertificate.objects.get(pk=self.prov3.id)

        assert prov1.remaining_energy_amount == 0
        assert prov2.remaining_energy_amount == 0
        assert prov3.remaining_energy_amount == 2000

        transfer_cert = ElecTransferCertificate.objects.all().first()
        assert transfer_cert.energy_amount == 500
        assert transfer_cert.supplier_id == self.cpo.id
        assert transfer_cert.client_id == self.operator.id

    def test_transfer_provision_certificate_multiple(self):
        self.client.post(
            reverse("elec-cpo-create-transfer-certificate"),
            {
                "entity_id": self.cpo.id,
                "energy_mwh": 1500,
                "client_id": self.operator.id,
            },
        )

        prov1 = ElecProvisionCertificate.objects.get(pk=self.prov1.id)
        prov2 = ElecProvisionCertificate.objects.get(pk=self.prov2.id)
        prov3 = ElecProvisionCertificate.objects.get(pk=self.prov3.id)

        assert prov1.remaining_energy_amount == 0
        assert prov2.remaining_energy_amount == 0
        assert prov3.remaining_energy_amount == 1000

        transfer_cert = ElecTransferCertificate.objects.all().first()
        assert transfer_cert.energy_amount == 1500
        assert transfer_cert.supplier_id == self.cpo.id
        assert transfer_cert.client_id == self.operator.id

    def test_transfer_provision_certificate_too_much(self):
        response = self.client.post(
            reverse("elec-cpo-create-transfer-certificate"),
            {
                "entity_id": self.cpo.id,
                "energy_mwh": 10000,
                "client_id": self.operator.id,
            },
        )

        assert response.status_code == 400
        assert response.json()["error"] == "NOT_ENOUGH_ENERGY"

        prov1 = ElecProvisionCertificate.objects.get(pk=self.prov1.id)
        prov2 = ElecProvisionCertificate.objects.get(pk=self.prov2.id)
        prov3 = ElecProvisionCertificate.objects.get(pk=self.prov3.id)

        assert prov1.remaining_energy_amount == 0
        assert prov2.remaining_energy_amount == 500
        assert prov3.remaining_energy_amount == 2000

        transfer_cert_count = ElecTransferCertificate.objects.count()
        assert transfer_cert_count == 0

    def test_cancel_transfer_certificate(self):
        self.client.post(
            reverse("elec-cpo-create-transfer-certificate"),
            {
                "entity_id": self.cpo.id,
                "energy_mwh": 1500,
                "client_id": self.operator.id,
            },
        )

        transfer = ElecTransferCertificate.objects.last()
        assert transfer.energy_amount == 1500

        response = self.client.post(
            reverse("elec-cpo-cancel-transfer-certificate"),
            {
                "entity_id": self.cpo.id,
                "transfer_certificate_id": transfer.id,
            },
        )

        assert response.status_code == 200

        prov1 = ElecProvisionCertificate.objects.get(pk=self.prov1.id)
        prov2 = ElecProvisionCertificate.objects.get(pk=self.prov2.id)
        prov3 = ElecProvisionCertificate.objects.get(pk=self.prov3.id)

        assert prov1.remaining_energy_amount == 0
        assert prov2.remaining_energy_amount == 500
        assert prov3.remaining_energy_amount == 2000

    def test_certificate_years(self):
        response = self.client.get(
            reverse("elec-cpo-certificate-years"),
            {
                "entity_id": self.cpo.id,
            },
        )

        json = response.json()
        assert json["data"] == [2022, 2023]

    def test_provision_certificate_filter(self):
        response = self.client.get(
            reverse("elec-cpo-provision-certificate-filters"),
            {
                "entity_id": self.cpo.id,
                "year": 2022,
                "filter": "operating_unit",
            },
        )

        assert response.status_code == 200
        json = response.json()

        assert json["data"]["filter_values"] == ["XYZ"]

        response = self.client.get(
            reverse("elec-cpo-provision-certificate-filters"),
            {
                "entity_id": self.cpo.id,
                "year": 2023,
                "filter": "operating_unit",
            },
        )

        assert response.status_code == 200
        json = response.json()

        assert json["data"]["filter_values"] == ["ABCD", "DCBA"]

    def test_provision_certificates(self):
        response = self.client.get(
            reverse("elec-cpo-get-provision-certificates"),
            {
                "entity_id": self.cpo.id,
                "year": 2022,
                "operating_unit": "XYZ",
                "from_idx": 0,
                "limit": 10,
            },
        )

        assert response.status_code == 200
        json = response.json()

        assert json["data"]["returned"] == 1
        assert json["data"]["elec_provision_certificates"][0]["operating_unit"] == "XYZ"

    def test_transfer_certificate_filter(self):
        ElecTransferCertificate.objects.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=1000,
            transfer_date=datetime.datetime(year=2023, month=6, day=2),
        )

        response = self.client.get(
            reverse("elec-cpo-get-transfer-certificate-filters"),
            {
                "entity_id": self.cpo.id,
                "year": 2023,
                "filter": "cpo",
            },
        )

        assert response.status_code == 200
        json = response.json()

        assert json["data"]["filter_values"] == [self.cpo.name]

        response = self.client.get(
            reverse("elec-cpo-get-transfer-certificate-filters"),
            {
                "entity_id": self.cpo.id,
                "year": 2023,
                "filter": "operator",
            },
        )

        assert response.status_code == 200
        json = response.json()

        assert json["data"]["filter_values"] == [self.operator.name]

    def test_transfer_certificates(self):
        ElecTransferCertificate.objects.create(
            supplier=self.cpo,
            status="PENDING",
            client=self.operator,
            energy_amount=1000,
            transfer_date=datetime.datetime(year=2023, month=6, day=2),
        )

        response = self.client.get(
            reverse("elec-cpo-get-transfer-certificates"),
            {
                "entity_id": self.cpo.id,
                "year": 2022,
                "from_idx": 0,
                "limit": 10,
            },
        )

        assert response.status_code == 200
        json = response.json()

        assert json["data"]["returned"] == 0

        response = self.client.get(
            reverse("elec-cpo-get-transfer-certificates"),
            {
                "entity_id": self.cpo.id,
                "year": 2023,
                "status": "PENDING",
                "from_idx": 0,
                "limit": 10,
            },
        )

        assert response.status_code == 200
        json = response.json()

        assert json["data"]["returned"] == 1
        assert json["data"]["elec_transfer_certificates"][0]["supplier"]["name"] == self.cpo.name
