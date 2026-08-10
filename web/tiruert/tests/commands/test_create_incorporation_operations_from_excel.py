import io
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from tiruert.management.commands.create_init_incorporation_operations_for_2027_period import Command
from tiruert.models import Operation


class CreateIncorporationOperationsFromExcelCommandTest(TestCase):
    def setUp(self):
        """Create the shared entity, feedstock and biofuel fixtures used by the tests."""
        self.entity = Entity.objects.create(name="Entity A", entity_type=Entity.OPERATOR)
        self.feedstock = MatierePremiere.objects.create(
            code="MP-1",
            name="Feedstock 1",
            name_en="Feedstock 1",
            description="",
            category=MatierePremiere.CONV,
        )
        self.biofuel = Biocarburant.objects.create(
            code="B100",
            name="Biofuel 1",
            name_en="Biofuel 1",
            description="",
            pci_litre=35.0,
            masse_volumique=0.8,
        )

    def _build_excel_bytes(self, rows):
        """Build an Excel file in memory from a list of rows for command execution."""
        buffer = io.BytesIO()
        pd.DataFrame(rows).to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue()

    def _call_command(self, rows, path="/tmp/test.xlsx"):
        """Invoke the management command against an in-memory Excel payload."""
        file_bytes = self._build_excel_bytes(rows)
        with patch(
            "tiruert.management.commands.create_init_incorporation_operations_for_2027_period.private_storage.open",
            return_value=io.BytesIO(file_bytes),
        ):
            return call_command(
                "create_init_incorporation_operations_for_2027_period",
                s3_path=path,
                stdout=StringIO(),
                stderr=StringIO(),
            )

    def test_creates_incorporation_operation_and_details_from_excel(self):
        """Create one incorporation operation and distribute the requested volume across eligible lots."""
        self.entity = Entity.objects.get(pk=self.entity.pk)

        lot1 = CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=100.0,
            biofuel=self.biofuel,
            feedstock=self.feedstock,
            carbure_client=self.entity,
            ghg_total=10.0,
        )
        lot2 = CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=200.0,
            biofuel=self.biofuel,
            feedstock=self.feedstock,
            carbure_client=self.entity,
            ghg_total=10.0,
        )

        rows = [
            {
                "entity_id": self.entity.id,
                "biofuel_code": self.biofuel.code,
                "customs_category": self.feedstock.category,
                "volume": 150.0,
            }
        ]

        self._call_command(rows)

        operation = Operation.objects.get(type=Operation.INCORPORATION)
        self.assertEqual(operation.credited_entity, self.entity)
        self.assertEqual(operation.details.count(), 2)
        self.assertEqual(operation.details.get(lot=lot1).volume, 100.0)
        self.assertEqual(operation.details.get(lot=lot2).volume, 50.0)

    def test_reports_all_validation_errors(self):
        """Report every validation error found in the uploaded rows."""
        rows = [
            {
                "entity_id": 999999,
                "biofuel_code": self.biofuel.code,
                "customs_category": self.feedstock.category,
                "volume": 10.0,
            },
            {
                "entity_id": self.entity.id,
                "biofuel_code": "UNKNOWN",
                "customs_category": self.feedstock.category,
                "volume": 10.0,
            },
            {
                "entity_id": self.entity.id,
                "biofuel_code": self.biofuel.code,
                "customs_category": "UNKNOWN_CATEGORY",
                "volume": 10.0,
            },
            {
                "entity_id": self.entity.id,
                "biofuel_code": self.biofuel.code,
                "customs_category": self.feedstock.category,
                "volume": 0.0,
            },
        ]

        with self.assertRaises(CommandError) as error:
            self._call_command(rows)

        message = str(error.exception)
        self.assertIn("Ligne 2", message)
        self.assertIn("entity_id", message)
        self.assertIn("Ligne 3", message)
        self.assertIn("biofuel_code", message)
        self.assertIn("Ligne 4", message)
        self.assertIn("customs_category", message)
        self.assertIn("Ligne 5", message)
        self.assertIn("volume", message)

    def test_selects_only_matching_lots(self):
        """Select only the lots matching the entity, biofuel and customs category."""
        matching_lot_1 = CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=120.0,
            biofuel=self.biofuel,
            feedstock=self.feedstock,
            carbure_client=self.entity,
            ghg_total=10.0,
        )
        matching_lot_2 = CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=80.0,
            biofuel=self.biofuel,
            feedstock=self.feedstock,
            carbure_client=self.entity,
            ghg_total=10.0,
        )

        other_biofuel = Biocarburant.objects.create(
            code="B200",
            name="Biofuel 2",
            name_en="Biofuel 2",
            description="",
            pci_litre=35.0,
            masse_volumique=0.8,
        )
        other_feedstock = MatierePremiere.objects.create(
            code="MP-2",
            name="Feedstock 2",
            name_en="Feedstock 2",
            description="",
            category=MatierePremiere.EP2AM,
        )

        CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=50.0,
            biofuel=other_biofuel,
            feedstock=self.feedstock,
            carbure_client=self.entity,
            ghg_total=10.0,
        )
        CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=60.0,
            biofuel=self.biofuel,
            feedstock=other_feedstock,
            carbure_client=self.entity,
            ghg_total=10.0,
        )
        other_entity = Entity.objects.create(name="Entity B", entity_type=Entity.OPERATOR)
        CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=70.0,
            biofuel=self.biofuel,
            feedstock=self.feedstock,
            carbure_client=other_entity,
            ghg_total=10.0,
        )
        CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=40.0,
            biofuel=self.biofuel,
            feedstock=self.feedstock,
            carbure_client=self.entity,
            ghg_total=10.0,
            lot_status=CarbureLot.REJECTED,
        )

        command = Command()
        selected_lots = list(command._get_lots(self.entity, self.biofuel, self.feedstock.category))

        self.assertEqual(selected_lots, [matching_lot_1, matching_lot_2])

    def test_calculates_ratio_from_requested_and_total_volume(self):
        """Compute the ratio from the requested volume and the total available volume."""
        command = Command()

        self.assertEqual(command._calculate_ratio(90.0, 200.0), 0.45)

    def test_calculates_volumes_by_filling_lots_in_order(self):
        """Fill the lots in order until the target volume is reached for a given group."""
        command = Command()
        lots = [
            SimpleNamespace(id=1, volume=120.0, ghg_total=10.0),
            SimpleNamespace(id=2, volume=80.0, ghg_total=10.0),
            SimpleNamespace(id=3, volume=200.0, ghg_total=10.0),
        ]

        result = command._calculate_lot_volumes(lots, 155.0)

        self.assertEqual(result, {1: 120.0, 2: 35.0})

    def test_creates_operation_details_with_expected_volume_and_ghg(self):
        """Create operation details that preserve the requested volume and the source GHG values."""
        lot_with_ghg_10 = CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=100.0,
            biofuel=self.biofuel,
            feedstock=self.feedstock,
            carbure_client=self.entity,
            ghg_total=10.0,
        )
        lot_with_ghg_15 = CarbureLot.objects.create(
            year=2026,
            period=1,
            volume=100.0,
            biofuel=self.biofuel,
            feedstock=self.feedstock,
            carbure_client=self.entity,
            ghg_total=15.0,
        )

        rows = [
            {
                "entity_id": self.entity.id,
                "biofuel_code": self.biofuel.code,
                "customs_category": self.feedstock.category,
                "volume": 150.0,
            }
        ]

        self._call_command(rows)

        operation = Operation.objects.get(type=Operation.INCORPORATION)
        details = operation.details.order_by("lot_id")

        # ratio = 150 / (100 + 100) = 0.75
        self.assertEqual(details.count(), 2)
        self.assertEqual(details.get(lot=lot_with_ghg_10).volume, 75.0)
        self.assertEqual(details.get(lot=lot_with_ghg_10).emission_rate_per_mj, 10.0)
        self.assertEqual(details.get(lot=lot_with_ghg_15).volume, 75.0)
        self.assertEqual(details.get(lot=lot_with_ghg_15).emission_rate_per_mj, 15.0)
