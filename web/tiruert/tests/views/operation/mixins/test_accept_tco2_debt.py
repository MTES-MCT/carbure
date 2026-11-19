from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import CarbureLot, MatierePremiere, UserRights
from core.tests_utils import setup_current_user
from tiruert.models import Operation, OperationDetail, TiruertDebt
from tiruert.services.correction import CorrectionService
from tiruert.tests.debt_utils import DebtTestMixin


class AcceptTransferCorrectionTest(DebtTestMixin, TestCase):
    def setUp(self):
        setup_current_user(self, "accept-debt@carbure.local", "Tester", "password", [(self.entity, UserRights.ADMIN)])

    def transfer(self, lot, volume=100, sender=None, category=MatierePremiere.CONV, rate=12.5, accepted=False):
        operation = Operation.objects.create(
            type=Operation.TRANSFERT,
            status=Operation.ACCEPTED if accepted else Operation.PENDING,
            biofuel=self.biofuel,
            customs_category=category,
            debited_entity=sender or self.entity,
            credited_entity=self.entity if sender else self.other_entity,
        )
        OperationDetail.objects.create(operation=operation, lot=lot, volume=volume, emission_rate_per_mj=rate)
        return operation

    def correct(self, lot, rate):
        CarbureLot.objects.filter(pk=lot.pk).update(ghg_total=rate)
        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])

    def accept(self, operation):
        return self.client.post(
            reverse("operations-accept", kwargs={"pk": operation.pk}),
            query_params={"entity_id": self.entity.id},
        )

    def debts(self):
        return TiruertDebt.objects.filter(type=TiruertDebt.TCO2).order_by("id")

    def test_accept_after_ghg_increase_does_not_create_debt(self):
        """A pending transfer is repriced during correction, before the recipient accepts it."""
        lot = self.create_lot()
        transfer = self.transfer(lot)
        detail = transfer.details.get()
        self.correct(lot, 22.5)
        self.assertFalse(self.debts().exists())
        detail.refresh_from_db()
        self.assertEqual(detail.emission_rate_per_mj_delta, 10)
        self.assertEqual(detail.effective_emission_rate_per_mj, 22.5)

        response = self.accept(transfer)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        detail.refresh_from_db()
        self.assertEqual((detail.volume, detail.emission_rate_per_mj, detail.emission_rate_per_mj_delta), (100, 12.5, 10))
        self.assertEqual(detail.effective_emission_rate_per_mj, 22.5)
        self.assertFalse(self.debts().exists())
        self.assertEqual(self.accept(transfer).status_code, status.HTTP_400_BAD_REQUEST)
