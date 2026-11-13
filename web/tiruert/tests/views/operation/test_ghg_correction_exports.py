from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook
from rest_framework import status

from core.models import Biocarburant, Entity
from core.tests_utils import setup_current_user
from tiruert.factories import OperationDetailFactory, OperationFactory
from tiruert.models import Operation
from transactions.factories import CarbureLotFactory


class GhgCorrectionExportsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.source = OperationFactory.create_incorporation(
            entity=cls.entity,
            biofuel=Biocarburant.objects.get(code="ETH"),
            status=Operation.CORRECTED,
            corrected=True,
        )
        cls.source_detail = OperationDetailFactory.create_for_operation(
            cls.source,
            lot=CarbureLotFactory.create(biofuel=cls.source.biofuel),
            volume=1000,
            emission_rate_per_mj=20,
            emission_rate_per_mj_delta=5,
        )

    def setUp(self):
        setup_current_user(self, "exports@carbure.local", "Exports", "gogogo", [(self.entity, "ADMIN")])

    def _export_rows(self, operation=None):
        url = (
            reverse("operations-export-operation-details-to-excel", kwargs={"pk": operation.pk})
            if operation is not None
            else reverse("operations-export-operations-to-excel")
        )
        response = self.client.get(url, {"entity_id": self.entity.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workbook = load_workbook(BytesIO(response.content), read_only=True, data_only=True)
        try:
            headers, *rows = workbook.active.iter_rows(values_only=True)
            return [dict(zip(headers, row)) for row in rows]
        finally:
            workbook.close()

    def _create_ghg_event(self):
        event = OperationFactory.create(
            type=Operation.CORRECTION,
            status=Operation.VALIDATED,
            credited_entity=self.entity,
            biofuel=self.source.biofuel,
        )
        OperationDetailFactory.create_for_operation(
            event,
            lot=self.source_detail.lot,
            volume=0,
            emission_rate_per_mj=20,
            emission_rate_per_mj_delta=5,
        )
        return event

    def test_operation_export_uses_corrected_emissions(self):
        """Corrected emissions, including zero and negative values, replace history in Excel."""
        for delta, expected in ((5, 1.44), (74, 0), (80, -0.12)):
            with self.subTest(delta=delta):
                self.source_detail.emission_rate_per_mj_delta = delta
                self.source_detail.save(update_fields=["emission_rate_per_mj_delta"])

                (row,) = self._export_rows()

                self.assertEqual(row["Tonnes CO2 eq. évitées"], expected)

    def test_operation_export_leaves_ghg_event_quantities_blank(self):
        """A GHG event has empty quantity cells rather than zero stock movements."""
        self._create_ghg_event()

        rows = self._export_rows()

        event_row = next(row for row in rows if row["Type Opération"] == Operation.CORRECTION)
        self.assertIsNone(event_row["Volume (L)"])
        self.assertIsNone(event_row["Énergie (MJ)"])
        self.assertIsNone(event_row["Tonnes CO2 eq. évitées"])

    def test_detail_export_uses_corrected_rate_and_emissions(self):
        """Corrected detail exports use effective rates even when emissions are zero."""
        for delta, rate, emissions in ((5, 25, 1.44), (74, 94, 0), (80, 100, -0.12)):
            with self.subTest(delta=delta):
                self.source_detail.emission_rate_per_mj_delta = delta
                self.source_detail.save(update_fields=["emission_rate_per_mj_delta"])

                (row,) = self._export_rows(self.source)

                self.assertEqual(row["Taux d'émission (gCO₂/MJ)"], rate)
                self.assertEqual(row["Émissions évitées (tCO₂)"], emissions)
                self.assertNotIn("Delta GES (gCO₂/MJ)", row)

    def test_detail_export_leaves_ghg_event_quantities_blank(self):
        """The event detail export also leaves volumes and avoided emissions empty."""
        event = self._create_ghg_event()

        (row,) = self._export_rows(event)

        self.assertIsNone(row["Volume prélevé (L)"])
        self.assertIsNone(row["Émissions évitées (tCO₂)"])

    def test_detail_export_exposes_event_delta_and_effective_rate(self):
        """A GHG event adds a delta column alongside its resulting emission rate."""
        event = self._create_ghg_event()

        (row,) = self._export_rows(event)

        self.assertEqual(row["Taux d'émission (gCO₂/MJ)"], 25)
        self.assertEqual(row["Delta GES (gCO₂/MJ)"], 5)
