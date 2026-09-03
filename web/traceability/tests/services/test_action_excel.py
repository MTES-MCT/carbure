from django.test import TestCase
from openpyxl import load_workbook

from traceability.services.action_excel import build_action_import_template, parse_action_import_file
from traceability.tests.excel import GENERIC_ROW, GenericExcelHandler, fill_action_template


class ActionExcelTemplateTest(TestCase):
    def test_template_headers_match_handler_columns(self):
        handler = GenericExcelHandler()
        file_handle = build_action_import_template(handler)
        workbook = load_workbook(filename=file_handle)
        file_handle.close()
        self.addCleanup(workbook.close)

        headers = [cell.value for cell in workbook["Import actions H2"][1]]
        self.assertEqual(headers, [column["header"] for column in handler.excel_columns])


class ParseActionImportFileTest(TestCase):
    def test_maps_headers_to_keys_and_ignores_unknown_columns(self):
        handler = GenericExcelHandler()
        buffer = fill_action_template(
            handler,
            GENERIC_ROW,
            extra_headers=[("Colonne inconnue", "valeur ignorée")],
        )

        rows = parse_action_import_file(buffer, handler)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["pos_id"], "ACT-001")
        self.assertEqual(rows[0]["material"], "Matière")
        self.assertEqual(rows[0]["etd"], 0)
        self.assertNotIn("Colonne inconnue", rows[0])
