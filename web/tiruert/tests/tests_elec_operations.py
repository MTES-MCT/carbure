from datetime import date

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from tiruert.models.elec_operation import ElecOperation
from tiruert.services.elec_operation import ElecOperationService


class ElecOperationTest(TestCase):
    fixtures = [
        "json/entities.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.cpo1 = Entity.objects.create(name="CPO 1", entity_type=Entity.CPO)
        self.cpo2 = Entity.objects.create(name="CPO 2", entity_type=Entity.CPO)
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        self.transfer_certificates = [
            ElecTransferCertificate.objects.create(
                supplier=self.cpo1,
                client=self.entity,
                transfer_date=date.today(),
                energy_amount=1000,
                status=ElecTransferCertificate.ACCEPTED,
            ),
            ElecTransferCertificate.objects.create(
                supplier=self.cpo2,
                client=self.entity,
                transfer_date=date.today(),
                energy_amount=9000,
                status=ElecTransferCertificate.ACCEPTED,
            ),
            ElecTransferCertificate.objects.create(
                supplier=self.cpo1,
                client=self.entity,
                transfer_date=date.today(),
                energy_amount=10000,
                status=ElecTransferCertificate.PENDING,
            ),
        ]

    def test_create_tiruert_operations_from_elec_certificates(self):
        operations = ElecOperation.objects.all()
        assert operations.count() == 0

        operation = ElecOperationService.update_operator_cpo_acquisition_operations(self.entity)

        assert operation is not None
        assert operation.quantity == 3600 * 10000
        assert operations.count() == 1

        operation = ElecOperationService.update_operator_cpo_acquisition_operations(self.entity)

        assert operations.count() == 1
        assert operation is None

    def test_view_operations(self):
        ElecOperationService.update_operator_cpo_acquisition_operations(self.entity)

        query = {
            "entity_id": self.entity.id,
        }
        response = self.client.get(reverse("elec-operations-list"), query)
        assert response.status_code == 200
        assert response.json()["count"] == 1
        data = response.json()["results"]
        assert list(data[0].keys()) == [
            "id",
            "type",
            "status",
            "credited_entity",
            "debited_entity",
            "quantity",
            "created_at",
        ]
