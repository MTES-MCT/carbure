from datetime import date
from decimal import Decimal
from io import BytesIO

from django.test import TestCase
from openpyxl import load_workbook

from core.models import Entity
from h2.handlers import H2ActionHandler
from traceability.factories import MaterialFactory
from traceability.models import Action
from traceability.services.action_excel import build_action_import_template, parse_action_import_file
from transactions.models import Site


def filled_h2_template(*, pos_id, material_name, site_name, shipping_date=date(2026, 1, 15), extra_headers=None):
    file_handle = build_action_import_template(H2ActionHandler())
    workbook = load_workbook(filename=BytesIO(file_handle.read()))
    file_handle.close()
    sheet = workbook["Import actions H2"]
    values = [
        pos_id,
        material_name,
        Decimal("120000.000"),
        site_name,
        shipping_date,
        25,
        Action.ROAD,
        0,
        0,
        0,
        0,
        0,
    ]
    for column, value in enumerate(values, start=1):
        sheet.cell(row=2, column=column, value=value)
    if extra_headers:
        start = len(H2ActionHandler.excel_columns) + 1
        for offset, (header, value) in enumerate(extra_headers):
            sheet.cell(row=1, column=start + offset, value=header)
            sheet.cell(row=2, column=start + offset, value=value)

    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    buffer.seek(0)
    return buffer


class ActionExcelTemplateTest(TestCase):
    def test_h2_template_uses_handler_columns_and_lookup_options(self):
        entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        hydrogen = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        MaterialFactory(code="BIO-WOOD", name="Bois")
        station = Site.objects.create(
            name="Station Paris",
            site_type=Site.H2_REFUELING_STATION,
            created_by=entity,
        )
        Site.objects.create(name="Dépôt Lyon", site_type=Site.EFS, created_by=entity)
        Site.objects.create(
            name="Station Lyon",
            site_type=Site.H2_REFUELING_STATION,
            created_by=Entity.objects.create(name="Other HRS", entity_type=Entity.HRS),
        )

        file_handle = build_action_import_template(H2ActionHandler(), entity)
        workbook = load_workbook(filename=BytesIO(file_handle.read()))
        file_handle.close()
        self.addCleanup(workbook.close)

        headers = [cell.value for cell in workbook["Import actions H2"][1]]
        references = workbook["References"]

        self.assertEqual(headers, [column["header"] for column in H2ActionHandler.excel_columns])
        self.assertEqual(references["B2"].value, hydrogen.name)
        self.assertIsNone(references["B3"].value)
        self.assertEqual(references["D2"].value, station.name)
        self.assertIsNone(references["D3"].value)


class ParseActionImportFileTest(TestCase):
    def test_maps_headers_to_keys_and_ignores_unknown_columns(self):
        buffer = filled_h2_template(
            pos_id="H2-001",
            material_name="Hydrogène gazeux",
            site_name="Station Paris",
            extra_headers=[("Producteur", "Air Liquide")],
        )

        rows = parse_action_import_file(buffer, H2ActionHandler())

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["pos_id"], "H2-001")
        self.assertEqual(rows[0]["material"], "Hydrogène gazeux")
        self.assertNotIn("Producteur", rows[0])
        self.assertNotIn("producer", rows[0])
