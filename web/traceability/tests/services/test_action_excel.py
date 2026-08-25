from io import BytesIO

from django.test import SimpleTestCase, TestCase
from openpyxl import load_workbook

from traceability.factories import MaterialFactory
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.h2 import H2ActionHandler
from traceability.models import Action
from traceability.services.action_excel import build_action_import_template


def load_template(handler, entity=None):
    file_handle = build_action_import_template(handler, entity)
    workbook = load_workbook(filename=BytesIO(file_handle.read()))
    file_handle.close()
    return workbook


class ActionExcelTemplateTest(SimpleTestCase):
    def test_default_columns_keep_generic_labels(self):
        workbook = load_template(ActionIndustryHandler())
        self.addCleanup(workbook.close)
        sheet = workbook[f"Import actions {None}"]
        references = workbook["References"]
        headers = [cell.value for cell in sheet[1]]

        self.assertEqual(headers[0], "N° de POS")
        self.assertEqual(headers[1], "Matière")
        self.assertEqual(headers[2], "Quantité")
        self.assertIsNone(references["B2"].value)
        self.assertEqual(
            [references.cell(row=row, column=6).value for row in range(2, 6)],
            [label for _, label in Action.SHIPPING_METHODS],
        )


class ActionExcelLookupColumnsTest(TestCase):
    def test_h2_handler_overrides_labels(self):
        workbook = load_template(H2ActionHandler())
        self.addCleanup(workbook.close)
        headers = [cell.value for cell in workbook["Import actions H2"][1]]

        self.assertEqual(headers[0], "N° de POS")
        self.assertEqual(headers[1], "Nature d'hydrogène")
        self.assertEqual(headers[2], "Quantité (MJ)")

    def test_h2_material_options_come_from_lookup(self):
        hydrogen = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        MaterialFactory(code="BIO-WOOD", name="Bois")

        workbook = load_template(H2ActionHandler())
        self.addCleanup(workbook.close)
        references = workbook["References"]

        self.assertEqual(references["B2"].value, hydrogen.name)
        self.assertIsNone(references["B3"].value)
