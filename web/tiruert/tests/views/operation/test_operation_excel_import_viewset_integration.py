from datetime import date
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.excel_importer import ExcelValidationError
from core.models import DeclarationPeriod, Entity
from core.tests_utils import setup_current_user
from tiruert.models import Operation
from tiruert.views.operation.mixins.excel_import import FILE_PROCESSING_ERROR, FILE_PROCESSING_ERROR_MESSAGE


class OperationExcelImportViewSetIntegrationTest(TestCase):
    """Integration tests for the operations Excel import endpoint wiring."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create a declaration period and select an operator entity for API tests."""
        current_year = date.today().year
        DeclarationPeriod.objects.create(
            year=current_year,
            start_date=date(current_year, 1, 1),
            end_date=date(current_year, 12, 31),
            app=DeclarationPeriod.TIRUERT,
        )

        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()

    def setUp(self):
        super().setUp()
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])
        self.url = reverse("operations-import-operations-from-excel")

    def _build_excel_upload(self):
        return SimpleUploadedFile(
            "operations_import.xlsx",
            b"dummy excel content",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    @patch("tiruert.views.operation.mixins.excel_import.OperationExcelImportService.execute")
    def test_import_operations_from_excel_post_wiring_calls_service_and_returns_payload(self, mock_execute):
        """Should wire POST /operations/import to the service and return its response payload as-is."""
        mock_execute.return_value = {
            "mode": "validate",
            "operations": [
                {
                    "operation_id": None,
                    "status": Operation.PENDING,
                    "type": Operation.TENEUR,
                    "sector": Operation.ESSENCE,
                    "customs_category": "CONV",
                    "biofuel": "ETH",
                    "debited_entity": {"id": self.entity.id, "name": self.entity.name},
                    "credited_entity": None,
                    "lot_count": 1,
                    "total_volume": 100.0,
                    "rows": [3],
                }
            ],
        }

        payload = {"file": self._build_excel_upload(), "mode": "validate"}

        response = self.client.post(self.url, data=payload, QUERY_STRING=f"entity_id={self.entity.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_execute.return_value)

        mock_execute.assert_called_once()
        called_file, called_mode, called_entity = mock_execute.call_args.args
        self.assertEqual(called_mode, "validate")
        self.assertEqual(called_entity.id, self.entity.id)
        self.assertEqual(called_file.name, "operations_import.xlsx")

    @patch("tiruert.views.operation.mixins.excel_import.OperationExcelImportService.execute")
    def test_import_operations_from_excel_post_error_wiring_returns_expected_400_payload(self, mock_execute):
        """Should convert ExcelValidationError from the service into the expected API 400 response contract."""
        validation_errors = [{"row": 3, "errors": {"validation": ["invalid volume"]}}]
        mock_execute.side_effect = ExcelValidationError(validation_errors, 1)

        payload = {"file": self._build_excel_upload(), "mode": "validate"}

        response = self.client.post(self.url, data=payload, QUERY_STRING=f"entity_id={self.entity.id}")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "validation_errors": validation_errors,
                "total_errors": 1,
                "total_rows_processed": 1,
            },
        )
        mock_execute.assert_called_once()

    @patch("tiruert.views.operation.mixins.excel_import.OperationExcelImportService.execute")
    def test_import_does_not_expose_internal_exception(self, mock_execute):
        mock_execute.side_effect = RuntimeError("secret parser crash")
        payload = {"file": self._build_excel_upload(), "mode": "validate"}

        response = self.client.post(self.url, data=payload, QUERY_STRING=f"entity_id={self.entity.id}")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "error": FILE_PROCESSING_ERROR,
                "message": FILE_PROCESSING_ERROR_MESSAGE,
            },
        )
        self.assertNotIn("secret", response.content.decode())
