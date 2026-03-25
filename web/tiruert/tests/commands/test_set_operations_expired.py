from datetime import date
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.test import TestCase

from core.models import Biocarburant, Entity, MatierePremiere
from tiruert.factories import OperationDetailFactory, OperationFactory
from tiruert.management.commands.set_operations_expired import Command
from tiruert.models import Operation, OperationDetail
from tiruert.models.declaration_period import TiruertDeclarationPeriod


class BaseExpirationTestCase(TestCase):
    """Shared fixtures and helpers for expiration tests."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        if not self.entity:
            self.entity, _ = Entity.objects.get_or_create(
                name="Test Entity",
                entity_type=Entity.OPERATOR,
            )

        self.biofuel = Biocarburant.objects.filter(compatible_essence=True).first()
        self.cmd = Command()

    def _create_incorporation(self, entity=None, volume=1000.0, emission_rate=10.0, **kwargs):
        """Create an INCORPORATION with a single OperationDetail. Returns (operation, detail)."""
        entity = entity or self.entity
        durability_period = kwargs.pop("durability_period", "202401")
        incorporation = OperationFactory.create_incorporation(
            entity=entity,
            biofuel=self.biofuel,
            durability_period=durability_period,
            **kwargs,
        )
        detail = OperationDetailFactory.create_for_operation(
            incorporation,
            volume=volume,
            emission_rate_per_mj=emission_rate,
        )
        return incorporation, detail

    def _get_lot_balance(self, entity, lot):
        """Compute available balance for a lot: sum(credits) - sum(debits) for confirmed statuses."""
        credits = OperationDetail.objects.filter(
            lot=lot,
            operation__credited_entity=entity,
            operation__status__in=Operation.CONFIRMED_STATUSES,
        ).aggregate(total=Coalesce(Sum(F("volume") * F("operation__renewable_energy_share")), 0.0))["total"]

        debits = OperationDetail.objects.filter(
            lot=lot,
            operation__debited_entity=entity,
            operation__status__in=Operation.CONFIRMED_STATUSES,
        ).aggregate(total=Coalesce(Sum(F("volume") * F("operation__renewable_energy_share")), 0.0))["total"]

        return round(credits - debits, 2)

    def _create_debit(self, entity, lot, volume, debit_type=Operation.TENEUR, status=Operation.DECLARED, **kwargs):
        """Create a debit operation (TENEUR, EXPORTATION, etc.) with a single detail."""
        debit = OperationFactory.create(
            type=debit_type,
            status=status,
            customs_category=MatierePremiere.CONV,
            biofuel=self.biofuel,
            credited_entity=None,
            debited_entity=entity,
            renewable_energy_share=kwargs.pop("renewable_energy_share", 1.0),
            **kwargs,
        )
        detail = OperationDetailFactory.create_for_operation(
            debit,
            lot=lot,
            volume=volume,
            emission_rate_per_mj=10.0,
        )
        return debit, detail


# Fixed date: the command checks date.today() - 1 day == period.end_date
FIXED_TODAY = date(2025, 4, 1)


class SetOperationsExpiredIntegrationTest(BaseExpirationTestCase):
    """Integration tests for the set_operations_expired management command end-to-end."""

    def setUp(self):
        super().setUp()

        # Declaration period: year=2025, end_date = FIXED_TODAY - 1 day
        self.period = TiruertDeclarationPeriod.objects.create(
            year=2025,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )

    def _call_command(self):
        """Call the management command with a frozen date and return stdout output."""
        with patch("tiruert.management.commands.set_operations_expired.date") as mock_date:
            mock_date.today.return_value = FIXED_TODAY
            out = StringIO()
            call_command("set_operations_expired", stdout=out)
            return out.getvalue()

    def test_no_period_closed_yesterday(self):
        """When no declaration period closed yesterday, no operations should be created."""
        self.period.delete()

        output = self._call_command()

        self.assertIn("No declaration period closed yesterday", output)
        self.assertFalse(Operation.objects.filter(type=Operation.EXPIRATION).exists())

    def test_no_credit_operations_for_expired_period(self):
        """When there are no credit operations for the expired period, nothing happens."""
        output = self._call_command()

        self.assertIn("No active confirmed operations found", output)
        self.assertFalse(Operation.objects.filter(type=Operation.EXPIRATION).exists())

    def test_creates_expiration_for_fully_unused_incorporation(self):
        """Full end-to-end: unused INCORPORATION gets fully expired."""
        incorporation, detail = self._create_incorporation(volume=1000.0)

        output = self._call_command()

        self.assertIn("Created 1 EXPIRATION operations", output)

        expiration = Operation.objects.filter(type=Operation.EXPIRATION).first()
        self.assertIsNotNone(expiration)
        self.assertEqual(expiration.status, Operation.ACCEPTED)
        self.assertEqual(expiration.debited_entity, self.entity)
        self.assertIsNone(expiration.credited_entity)
        self.assertEqual(expiration.biofuel, self.biofuel)
        self.assertEqual(expiration.customs_category, MatierePremiere.CONV)
        self.assertEqual(expiration.durability_period, "2024")
        self.assertEqual(expiration.renewable_energy_share, 1)

        exp_details = OperationDetail.objects.filter(operation=expiration)
        self.assertEqual(exp_details.count(), 1)
        self.assertEqual(exp_details.first().volume, 1000.0)
        self.assertEqual(exp_details.first().lot_id, detail.lot_id)
        self.assertEqual(exp_details.first().emission_rate_per_mj, 10.0)

    def test_creates_expiration_only_for_remaining_volume(self):
        """Partial consumption: only the remaining volume is expired."""
        _, detail = self._create_incorporation(volume=1000.0)
        lot = detail.lot

        self._create_debit(self.entity, lot, volume=600.0)

        output = self._call_command()

        self.assertIn("Created 1 EXPIRATION operations", output)

        exp_details = OperationDetail.objects.filter(operation__type=Operation.EXPIRATION)
        self.assertEqual(exp_details.count(), 1)
        self.assertEqual(exp_details.first().volume, 400.0)

    def test_no_expiration_when_volume_fully_consumed(self):
        """When all volume has been consumed by debits, no EXPIRATION should be created."""
        _, detail = self._create_incorporation(volume=1000.0)
        lot = detail.lot

        self._create_debit(self.entity, lot, volume=1000.0)

        output = self._call_command()

        self.assertIn("Created 0 EXPIRATION operations", output)
        self.assertFalse(Operation.objects.filter(type=Operation.EXPIRATION).exists())

    def test_idempotency_skips_if_already_expired(self):
        """Running the command twice should not create duplicate EXPIRATION operations."""
        self._create_incorporation(volume=500.0)

        self._call_command()
        self.assertEqual(Operation.objects.filter(type=Operation.EXPIRATION).count(), 1)

        output = self._call_command()
        self.assertIn("already exist", output)
        self.assertEqual(Operation.objects.filter(type=Operation.EXPIRATION).count(), 1)

    def test_multiple_lots_same_biofuel_grouped(self):
        """Multiple lots with the same biofuel/category produce a single EXPIRATION operation."""
        self._create_incorporation(volume=500.0)
        self._create_incorporation(volume=300.0, emission_rate=12.0)

        self._call_command()

        expirations = Operation.objects.filter(type=Operation.EXPIRATION)
        self.assertEqual(expirations.count(), 1)

        exp_details = OperationDetail.objects.filter(operation__type=Operation.EXPIRATION)
        self.assertEqual(exp_details.count(), 2)
        total_expired = sum(d.volume for d in exp_details)
        self.assertEqual(total_expired, 800.0)

    def test_handles_multiple_entities(self):
        """Different entities with remaining volume each get EXPIRATION operations."""
        entity2, _ = Entity.objects.get_or_create(name="Test Entity 2", entity_type=Entity.OPERATOR)

        self._create_incorporation(entity=self.entity, volume=1000.0)
        self._create_incorporation(entity=entity2, volume=500.0, emission_rate=12.0)

        self._call_command()

        expirations = Operation.objects.filter(type=Operation.EXPIRATION)
        self.assertEqual(expirations.count(), 2)

        exp1 = expirations.filter(debited_entity=self.entity).first()
        self.assertIsNotNone(exp1)
        self.assertEqual(OperationDetail.objects.filter(operation=exp1).first().volume, 1000.0)

        exp2 = expirations.filter(debited_entity=entity2).first()
        self.assertIsNotNone(exp2)
        self.assertEqual(OperationDetail.objects.filter(operation=exp2).first().volume, 500.0)

    def test_handles_cession_transferred_lots(self):
        """Ceded lots: both cedant and cessionnaire get appropriate EXPIRATION volumes."""
        entity_b, _ = Entity.objects.get_or_create(name="Entity B", entity_type=Entity.OPERATOR)

        _, detail = self._create_incorporation(volume=1000.0)
        lot = detail.lot

        # Entity A cedes 400L to Entity B
        cession = OperationFactory.create_cession(
            debited_entity=self.entity,
            credited_entity=entity_b,
            status=Operation.ACCEPTED,
            biofuel=self.biofuel,
        )
        OperationDetailFactory.create_for_operation(cession, lot=lot, volume=400.0, emission_rate_per_mj=10.0)

        self._call_command()

        # Entity A: 1000 credited - 400 ceded = 600 expired
        exp_a = Operation.objects.filter(type=Operation.EXPIRATION, debited_entity=self.entity).first()
        self.assertIsNotNone(exp_a)
        self.assertEqual(OperationDetail.objects.filter(operation=exp_a, lot=lot).first().volume, 600.0)

        # Entity B: 400 credited by cession → 400 expired
        exp_b = Operation.objects.filter(type=Operation.EXPIRATION, debited_entity=entity_b).first()
        self.assertIsNotNone(exp_b)
        self.assertEqual(OperationDetail.objects.filter(operation=exp_b, lot=lot).first().volume, 400.0)

    def test_renewable_energy_share_handled_correctly(self):
        """Source operation with RES != 1: effective volume accounts for it."""
        self._create_incorporation(volume=1000.0, renewable_energy_share=0.5)

        self._call_command()

        # Effective credit = 1000 * 0.5 = 500 → EXPIRATION volume = 500 with RES=1
        exp_detail = OperationDetail.objects.filter(operation__type=Operation.EXPIRATION).first()
        self.assertIsNotNone(exp_detail)
        self.assertEqual(exp_detail.volume, 500.0)
        self.assertEqual(exp_detail.operation.renewable_energy_share, 1)

    def test_different_biofuels_create_separate_expirations(self):
        """Operations with different biofuels produce separate EXPIRATION operations."""
        biofuel2 = Biocarburant.objects.filter(compatible_diesel=True).first()

        self._create_incorporation(volume=500.0)

        inc2 = OperationFactory.create_incorporation(
            entity=self.entity,
            biofuel=biofuel2,
            durability_period="202401",
        )
        OperationDetailFactory.create_for_operation(inc2, volume=300.0, emission_rate_per_mj=12.0)

        self._call_command()

        expirations = Operation.objects.filter(type=Operation.EXPIRATION)
        self.assertEqual(expirations.count(), 2)
        self.assertTrue(expirations.filter(biofuel=self.biofuel).exists())
        self.assertTrue(expirations.filter(biofuel=biofuel2).exists())

    def test_2024_volumes_expired_but_2025_untouched(self):
        """After running the command, 2024 incorporations are fully expired but 2025 remain available."""
        _, detail_2024 = self._create_incorporation(volume=1000.0, durability_period="202401")
        lot_2024 = detail_2024.lot

        _, detail_2025 = self._create_incorporation(volume=800.0, durability_period="202501")
        lot_2025 = detail_2025.lot

        self._call_command()

        # 2024 lot: balance should be 0 (credit 1000 - expiration 1000)
        self.assertEqual(self._get_lot_balance(self.entity, lot_2024), 0)

        # 2025 lot: no EXPIRATION, balance should be full 800
        self.assertFalse(OperationDetail.objects.filter(operation__type=Operation.EXPIRATION, lot=lot_2025).exists())
        self.assertEqual(self._get_lot_balance(self.entity, lot_2025), 800.0)

    def test_confirmed_debit_on_2024_reduces_expiration_volume(self):
        """A confirmed debit on a 2024 lot reduces the EXPIRATION volume, and zeroes the balance."""
        _, detail_2024 = self._create_incorporation(volume=1000.0, durability_period="202401")
        lot_2024 = detail_2024.lot

        _, detail_2025 = self._create_incorporation(volume=800.0, durability_period="202501")
        lot_2025 = detail_2025.lot

        # Confirmed debit consuming 400L from the 2024 lot
        self._create_debit(self.entity, lot_2024, volume=400.0, status=Operation.ACCEPTED)

        self._call_command()

        # EXPIRATION = 1000 - 400 = 600
        exp_detail = OperationDetail.objects.filter(operation__type=Operation.EXPIRATION, lot=lot_2024).first()
        self.assertIsNotNone(exp_detail)
        self.assertEqual(exp_detail.volume, 600.0)

        # 2024 balance: credit(1000) - debit(400) - expiration(600) = 0
        self.assertEqual(self._get_lot_balance(self.entity, lot_2024), 0)

        # 2025 untouched
        self.assertEqual(self._get_lot_balance(self.entity, lot_2025), 800.0)

    def test_pending_draft_debit_on_2024_canceled_before_expiration(self):
        """PENDING/DRAFT debits on 2024 lots are canceled by the command and don't reduce EXPIRATION."""
        _, detail_2024 = self._create_incorporation(volume=1000.0, durability_period="202401")
        lot_2024 = detail_2024.lot

        _, detail_2025 = self._create_incorporation(volume=800.0, durability_period="202501")
        lot_2025 = detail_2025.lot

        # PENDING debit on 2024 lot — should be canceled by the command
        pending_debit, _ = self._create_debit(self.entity, lot_2024, volume=400.0, status=Operation.PENDING)

        self._call_command()

        # The PENDING debit should now be CANCELED
        pending_debit.refresh_from_db()
        self.assertEqual(pending_debit.status, Operation.CANCELED)

        # EXPIRATION should be for the full 1000 (PENDING debit was canceled)
        exp_detail = OperationDetail.objects.filter(operation__type=Operation.EXPIRATION, lot=lot_2024).first()
        self.assertIsNotNone(exp_detail)
        self.assertEqual(exp_detail.volume, 1000.0)

        # 2024 balance = 0 (credit 1000 - expiration 1000, canceled debit excluded)
        self.assertEqual(self._get_lot_balance(self.entity, lot_2024), 0)

        # 2025 untouched
        self.assertEqual(self._get_lot_balance(self.entity, lot_2025), 800.0)

    def test_debit_on_2025_does_not_affect_2024_expiration(self):
        """A debit on a 2025 lot has no impact on the 2024 EXPIRATION calculation."""
        _, detail_2024 = self._create_incorporation(volume=1000.0, durability_period="202401")
        lot_2024 = detail_2024.lot

        _, detail_2025 = self._create_incorporation(volume=800.0, durability_period="202501")
        lot_2025 = detail_2025.lot

        # Confirmed debit on 2025 lot (not related to 2024 expiration)
        self._create_debit(self.entity, lot_2025, volume=300.0, status=Operation.DECLARED)

        self._call_command()

        # 2024: full EXPIRATION of 1000 (2025 debit is irrelevant)
        exp_detail = OperationDetail.objects.filter(operation__type=Operation.EXPIRATION, lot=lot_2024).first()
        self.assertIsNotNone(exp_detail)
        self.assertEqual(exp_detail.volume, 1000.0)
        self.assertEqual(self._get_lot_balance(self.entity, lot_2024), 0)

        # 2025: no EXPIRATION, balance = 800 - 300 = 500
        self.assertFalse(OperationDetail.objects.filter(operation__type=Operation.EXPIRATION, lot=lot_2025).exists())
        self.assertEqual(self._get_lot_balance(self.entity, lot_2025), 500.0)
