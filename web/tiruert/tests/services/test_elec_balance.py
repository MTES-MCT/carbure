from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import Entity
from entity.factories import EntityFactory
from tiruert.factories import ElecOperationFactory
from tiruert.models import ElecOperation
from tiruert.services.elec_balance import ElecBalanceService


class ElecBalanceServiceTest(TestCase):
    def setUp(self):
        self.operator = EntityFactory(entity_type=Entity.OPERATOR, has_elec=True)

    def test_calculate_balance_with_date_filters(self):
        now = timezone.now()
        old_time = now - timedelta(days=10)
        recent_time = now - timedelta(days=2)
        date_from = now - timedelta(days=5)

        credit_old = ElecOperationFactory.create_credit(
            self.operator,
            quantity=100,
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
        )
        credit_recent = ElecOperationFactory.create_credit(
            self.operator,
            quantity=60,
            type=ElecOperation.ACQUISITION_FROM_CPO,
            status=ElecOperation.ACCEPTED,
        )
        debit_old = ElecOperationFactory.create_debit(
            self.operator,
            quantity=40,
            status=ElecOperation.ACCEPTED,
        )
        pending_teneur = ElecOperationFactory.create_teneur(
            self.operator,
            quantity=5,
            status=ElecOperation.PENDING,
        )
        declared_teneur = ElecOperationFactory.create_teneur(
            self.operator,
            quantity=3,
            status=ElecOperation.DECLARED,
        )
        pending_cession = ElecOperationFactory.create_debit(
            self.operator,
            quantity=12,
            status=ElecOperation.PENDING,
        )

        ElecOperation.objects.filter(id__in=[credit_old.id, debit_old.id, pending_cession.id]).update(created_at=old_time)
        ElecOperation.objects.filter(id__in=[credit_recent.id, pending_teneur.id, declared_teneur.id]).update(
            created_at=recent_time
        )

        balance = ElecBalanceService.calculate_balance(
            ElecOperation.objects.all(),
            entity_id=self.operator.id,
            date_from=date_from,
        )

        self.assertEqual(balance["sector"], ElecOperation.SECTOR)
        self.assertEqual(balance["emission_rate_per_mj"], ElecOperation.EMISSION_RATE_PER_MJ)
        self.assertEqual(balance["quantity"]["credit"], 60)
        self.assertEqual(balance["quantity"]["debit"], 8)
        self.assertEqual(balance["pending_operations"], 2)
        self.assertEqual(balance["pending_teneur"], 5)
        self.assertEqual(balance["declared_teneur"], 3)
        self.assertEqual(balance["available_balance"], 100)

    def test_calculate_balance_returns_zero_when_no_operations(self):
        balance = ElecBalanceService.calculate_balance(ElecOperation.objects.none(), entity_id=self.operator.id)

        self.assertEqual(balance["quantity"]["credit"], 0)
        self.assertEqual(balance["quantity"]["debit"], 0)
        self.assertEqual(balance["pending_operations"], 0)
        self.assertEqual(balance["pending_teneur"], 0)
        self.assertEqual(balance["declared_teneur"], 0)
        self.assertEqual(balance["available_balance"], 0)

    def test_calculate_balance_without_date_filters_mixed_statuses(self):
        ElecOperationFactory.create_credit(
            self.operator,
            quantity=100,
            status=ElecOperation.ACCEPTED,
        )
        ElecOperationFactory.create_credit(
            self.operator,
            quantity=20,
            status=ElecOperation.PENDING,
        )
        ElecOperationFactory.create_debit(
            self.operator,
            quantity=30,
            status=ElecOperation.ACCEPTED,
        )
        ElecOperationFactory.create_debit(
            self.operator,
            quantity=5,
            status=ElecOperation.PENDING,
        )
        ElecOperationFactory.create_teneur(
            self.operator,
            quantity=3,
            status=ElecOperation.PENDING,
        )
        ElecOperationFactory.create_teneur(
            self.operator,
            quantity=7,
            status=ElecOperation.DECLARED,
        )

        balance = ElecBalanceService.calculate_balance(
            ElecOperation.objects.all(),
            entity_id=self.operator.id,
        )

        self.assertEqual(balance["quantity"]["credit"], 100)
        self.assertEqual(balance["quantity"]["debit"], 45)
        self.assertEqual(balance["pending_operations"], 3)
        self.assertEqual(balance["pending_teneur"], 3)
        self.assertEqual(balance["declared_teneur"], 7)
        self.assertEqual(balance["available_balance"], 55)

    def test_calculate_balance_ignores_other_entities_and_rejected(self):
        other_entity = EntityFactory(entity_type=Entity.OPERATOR, has_elec=True)

        # Should count
        ElecOperationFactory.create_credit(
            self.operator,
            quantity=60,
            status=ElecOperation.ACCEPTED,
        )
        ElecOperationFactory.create_debit(
            self.operator,
            quantity=10,
            status=ElecOperation.ACCEPTED,
        )

        # Should be excluded: wrong entity
        ElecOperationFactory.create_credit(
            other_entity,
            quantity=100,
            status=ElecOperation.ACCEPTED,
        )
        # Should be excluded: rejected/canceled
        ElecOperationFactory.create_credit(
            self.operator,
            quantity=200,
            status=ElecOperation.REJECTED,
        )
        ElecOperationFactory.create_debit(
            self.operator,
            quantity=50,
            status=ElecOperation.CANCELED,
        )

        balance = ElecBalanceService.calculate_balance(
            ElecOperation.objects.all(),
            entity_id=self.operator.id,
        )

        self.assertEqual(balance["quantity"]["credit"], 60)
        self.assertEqual(balance["quantity"]["debit"], 10)
        self.assertEqual(balance["available_balance"], 50)
