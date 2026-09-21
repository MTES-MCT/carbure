from datetime import date, datetime, timezone
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from core.models import Biocarburant, Entity, MatierePremiere
from tiruert.factories import OperationDetailFactory, OperationFactory
from tiruert.models import Operation, OperationDetail
from tiruert.models.declaration_period import TiruertDeclarationPeriod
from tiruert.services.balance import BalanceService

# Fixed date: the command checks date.today() - 1 day == period.end_date
FIXED_TODAY = date(2026, 4, 1)
DEFAULT_OPERATION_CREATED_AT = datetime(2026, 3, 30, tzinfo=timezone.utc)


class CreateYearlyBalanceOperationsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.biofuel = Biocarburant.objects.filter(compatible_essence=True).first()
        self.period = TiruertDeclarationPeriod.objects.create(
            year=2025,
            start_date=date(2025, 4, 1),
            end_date=date(2026, 3, 31),
        )

    def _call_command(self, fixed_today=FIXED_TODAY):
        current_declaration_year = fixed_today.year
        with (
            patch("tiruert.management.commands.create_yearly_balance_operations.date") as mock_date,
            patch(
                "tiruert.management.commands.create_yearly_balance_operations.DeclarationPeriodService.get_current_declaration_year",
                return_value=current_declaration_year,
            ),
        ):
            mock_date.today.return_value = fixed_today
            out = StringIO()
            call_command("create_yearly_balance_operations", stdout=out)
            return out.getvalue()

    def _create_incorporation(self, volume=1000.0, entity=None, created_at=DEFAULT_OPERATION_CREATED_AT):
        operation = OperationFactory.create_incorporation(
            entity=entity or self.entity,
            biofuel=self.biofuel,
            durability_period="202501",
        )
        operation.created_at = created_at
        operation.save(update_fields=["created_at"])

        detail = OperationDetailFactory.create_for_operation(
            operation,
            volume=volume,
            emission_rate_per_mj=10.0,
        )
        return operation, detail

    def _create_teneur(self, lot, volume, entity=None, created_at=DEFAULT_OPERATION_CREATED_AT):
        operation = OperationFactory.create(
            type=Operation.TENEUR,
            status=Operation.DECLARED,
            customs_category=MatierePremiere.CONV,
            biofuel=self.biofuel,
            credited_entity=None,
            debited_entity=entity or self.entity,
            renewable_energy_share=1.0,
        )
        operation.created_at = created_at
        operation.save(update_fields=["created_at"])

        OperationDetailFactory.create_for_operation(operation, lot=lot, volume=volume, emission_rate_per_mj=10.0)
        return operation

    def test_no_period_closed_yesterday(self):
        self.period.delete()
        self._create_incorporation()

        output = self._call_command()

        self.assertIn("No declaration period closed yesterday", output)
        self.assertFalse(Operation.objects.filter(type=Operation.YEARLY_BALANCE).exists())

    def test_snapshot_created_for_remaining_balance(self):
        _, detail = self._create_incorporation(volume=1000.0)
        self._create_teneur(detail.lot, 400.0)

        self._call_command()

        snapshot = Operation.objects.get(type=Operation.YEARLY_BALANCE)
        self.assertEqual(snapshot.declaration_year, 2026)
        self.assertEqual(snapshot.status, Operation.AUTO)
        self.assertEqual(snapshot.credited_entity, self.entity)
        self.assertEqual(snapshot.biofuel, self.biofuel)
        self.assertEqual(snapshot.customs_category, MatierePremiere.CONV)
        self.assertEqual(snapshot.volume, 600.0)

        details = OperationDetail.objects.filter(operation=snapshot)
        self.assertEqual(details.count(), 1)
        self.assertIsNone(details.first().lot_id)

    def test_snapshot_uses_current_declaration_year(self):
        self._create_incorporation(volume=500.0)

        self._call_command()

        snapshot = Operation.objects.get(type=Operation.YEARLY_BALANCE)
        self.assertEqual(snapshot.declaration_year, self.period.year + 1)

    def test_no_snapshot_when_balance_is_empty(self):
        _, detail = self._create_incorporation(volume=1000.0)
        self._create_teneur(detail.lot, 1000.0)

        self._call_command()

        self.assertTrue(Operation.objects.filter(type=Operation.YEARLY_BALANCE).exists())
        self.assertEqual(Operation.objects.get(type=Operation.YEARLY_BALANCE).volume, 0.0)

    def test_no_snapshot_when_balance_is_negative(self):
        _, detail = self._create_incorporation(volume=1000.0)
        self._create_teneur(detail.lot, 1001.0)

        self._call_command()

        self.assertFalse(Operation.objects.filter(type=Operation.YEARLY_BALANCE).exists())

    def test_command_is_idempotent(self):
        self._create_incorporation(volume=1000.0)

        self._call_command()
        output = self._call_command()

        self.assertIn("already exist", output)
        self.assertEqual(Operation.objects.filter(type=Operation.YEARLY_BALANCE).count(), 1)

    def test_snapshot_is_not_counted_in_next_snapshot(self):
        self._create_incorporation(volume=1000.0, created_at=datetime(2025, 3, 30, tzinfo=timezone.utc))
        TiruertDeclarationPeriod.objects.create(
            year=2024,
            start_date=date(2024, 4, 1),
            end_date=date(2025, 3, 31),
        )

        self._call_command(fixed_today=date(2025, 4, 1))
        self._call_command(fixed_today=FIXED_TODAY)

        snapshot_2025 = Operation.objects.get(type=Operation.YEARLY_BALANCE, declaration_year=2025)
        self.assertEqual(snapshot_2025.volume, 1000.0)

        snapshot_2026 = Operation.objects.get(type=Operation.YEARLY_BALANCE, declaration_year=2026)
        self.assertEqual(snapshot_2026.volume, 1000.0)

    def test_snapshot_excludes_operations_after_period_end_date(self):
        self._create_incorporation(volume=1000.0)

        self._create_incorporation(volume=700.0, created_at=datetime(2026, 4, 1, tzinfo=timezone.utc))

        self._call_command()

        snapshot = Operation.objects.get(type=Operation.YEARLY_BALANCE, declaration_year=2026)
        self.assertEqual(snapshot.volume, 1000.0)

    def test_snapshot_is_excluded_from_balance(self):
        self._create_incorporation(volume=1000.0)

        self._call_command()
        snapshot = Operation.objects.get(type=Operation.YEARLY_BALANCE)
        self.assertEqual(snapshot.volume, 1000.0)

        balance = BalanceService.calculate_balance(Operation.objects.all(), self.entity.id, None, "l")
        total = sum(entry["available_balance"] for entry in balance.values())
        self.assertEqual(total, 1000.0)

    def test_one_snapshot_per_biofuel_and_category(self):
        other_biofuel = Biocarburant.objects.filter(compatible_diesel=True).exclude(id=self.biofuel.id).first()
        self._create_incorporation(volume=1000.0)
        operation = OperationFactory.create_incorporation(
            entity=self.entity,
            biofuel=other_biofuel,
            durability_period="202501",
        )
        operation.created_at = DEFAULT_OPERATION_CREATED_AT
        operation.save(update_fields=["created_at"])
        OperationDetailFactory.create_for_operation(operation, volume=200.0, emission_rate_per_mj=10.0)

        self._call_command()

        self.assertEqual(Operation.objects.filter(type=Operation.YEARLY_BALANCE).count(), 2)
