from datetime import date
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from core.models import Biocarburant, Entity
from tiruert.factories import OperationFactory
from tiruert.models import Operation
from tiruert.models.declaration_period import TiruertDeclarationPeriod

FIXED_TODAY = date(2026, 4, 1)


class CancelClosedPeriodOperationsCommandTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/entities.json",
        "json/countries.json",
        "json/feedstock.json",
    ]

    def setUp(self):
        self.biofuel = Biocarburant.objects.filter(compatible_essence=True).first()
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.period = TiruertDeclarationPeriod.objects.create(
            year=2025,
            start_date=date(2025, 4, 1),
            end_date=date(2026, 3, 31),
        )

    def _call_command(self):
        with patch("tiruert.management.commands.cancel_closed_period_operations.date") as mock_date:
            mock_date.today.return_value = FIXED_TODAY
            out = StringIO()
            call_command("cancel_closed_period_operations", stdout=out)
            return out.getvalue()

    def test_api_deletable_types_values_are_fixed(self):
        self.assertEqual(
            Operation.API_DELETABLE_TYPES,
            [
                Operation.TRANSFERT,
                Operation.EXPORTATION,
                Operation.EXPEDITION,
                Operation.TENEUR,
                Operation.DEVALUATION,
                Operation.CESSION,
            ],
        )

    def test_no_period_closed_yesterday(self):
        self.period.delete()

        output = self._call_command()

        self.assertIn("No declaration period closed yesterday", output)
        self.assertFalse(Operation.objects.filter(status=Operation.CANCELED).exists())

    def test_cancels_operations_and_reports_counts_by_type(self):
        OperationFactory.create(
            type=Operation.TENEUR,
            status=Operation.PENDING,
            declaration_year=self.period.year,
            biofuel=self.biofuel,
            credited_entity=self.entity,
        )
        OperationFactory.create(
            type=Operation.TENEUR,
            status=Operation.DRAFT,
            declaration_year=self.period.year,
            biofuel=self.biofuel,
            credited_entity=self.entity,
        )
        OperationFactory.create(
            type=Operation.CESSION,
            status=Operation.PENDING,
            declaration_year=self.period.year,
            biofuel=self.biofuel,
            credited_entity=self.entity,
            debited_entity=self.entity,
        )
        OperationFactory.create(
            type=Operation.TRANSFERT,
            status=Operation.DRAFT,
            declaration_year=self.period.year,
            biofuel=self.biofuel,
            credited_entity=self.entity,
        )

        output = self._call_command()

        self.assertIn("4 operations have been canceled for declaration year 2025.", output)
        self.assertIn("- CESSION: 1 operation(s) canceled", output)
        self.assertIn("- TENEUR: 2 operation(s) canceled", output)
        self.assertIn("- TRANSFERT: 1 operation(s) canceled", output)
        self.assertEqual(
            Operation.objects.filter(
                declaration_year=self.period.year,
                type__in=Operation.API_DELETABLE_TYPES,
                status=Operation.CANCELED,
            ).count(),
            4,
        )
