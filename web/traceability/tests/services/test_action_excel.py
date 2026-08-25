from io import BytesIO

from django.test import SimpleTestCase, TestCase
from openpyxl import load_workbook

from traceability.factories import MaterialFactory
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.h2 import H2ActionHandler
from traceability.models import Action
from traceability.services.action_excel import build_action_import_template
from transactions.models import Site


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

        self.assertEqual(
            headers,
            [column["header"] for column in ActionIndustryHandler.excel_columns],
        )
        self.assertIsNone(references["B2"].value)
        self.assertIsNone(references["D2"].value)
        self.assertEqual(
            [references.cell(row=row, column=7).value for row in range(2, 6)],
            [value for value, _ in Action.SHIPPING_METHODS],
        )


class ActionExcelLookupColumnsTest(TestCase):
    def test_h2_template_uses_handler_columns(self):
        workbook = load_template(H2ActionHandler())
        self.addCleanup(workbook.close)
        headers = [cell.value for cell in workbook["Import actions H2"][1]]

        self.assertEqual(headers, [column["header"] for column in H2ActionHandler.excel_columns])

    def test_h2_material_options_come_from_lookup(self):
        hydrogen = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        MaterialFactory(code="BIO-WOOD", name="Bois")

        workbook = load_template(H2ActionHandler())
        self.addCleanup(workbook.close)
        references = workbook["References"]

        self.assertEqual(references["B2"].value, hydrogen.name)
        self.assertIsNone(references["B3"].value)

    def test_h2_site_options_come_from_lookup(self):
        station = Site.objects.create(name="Station Paris", site_type=Site.H2_REFUELING_STATION)
        Site.objects.create(name="Dépôt Lyon", site_type=Site.EFS)

        workbook = load_template(H2ActionHandler())
        self.addCleanup(workbook.close)
        references = workbook["References"]

        self.assertEqual(references["D2"].value, station.name)
        self.assertIsNone(references["D3"].value)
