from datetime import date
from decimal import Decimal
from io import BytesIO

from django.test import TestCase
from openpyxl import load_workbook

from core.import_export_template import get_data_start_row
from core.models import Entity
from core.models.certificate import GenericCertificate
from h2.handlers import H2ActionHandler
from traceability.factories import MaterialFactory
from traceability.models import Action
from traceability.services.action_excel import build_action_import_template, parse_action_import_file
from transactions.factories.certificate import GenericCertificateFactory
from transactions.models import Site


def filled_h2_template(
    *,
    pos_id,
    material_name,
    site_name,
    certificate_id="",
    lot_id="LOT-001",
    producer="Air Liquide",
    batch_id="BATCH-001",
    shipping_date=date(2026, 1, 15),
    working_date=date(2026, 2, 1),
    extra_headers=None,
):
    file_handle = build_action_import_template(H2ActionHandler())
    workbook = load_workbook(filename=BytesIO(file_handle.read()))
    file_handle.close()
    sheet = workbook["Import actions H2"]
    values_by_key = {
        "lot_id": lot_id,
        "producer": producer,
        "batch_id": batch_id,
        "pos_id": pos_id,
        "material": material_name,
        "certificate": certificate_id,
        "quantity": Decimal("120000.000"),
        "site": site_name,
        "shipping_date": shipping_date,
        "shipping_distance": 25,
        "shipping_method": Action.ROAD,
        "working_date": working_date,
        "ei": 0,
        "ep": 0,
        "etd": 0,
        "eu": 0,
        "eccs": 0,
    }
    data_row = get_data_start_row(H2ActionHandler.excel_columns)
    for column, spec in enumerate(H2ActionHandler.excel_columns, start=1):
        key = spec.get("key")
        if key:
            sheet.cell(row=data_row, column=column, value=values_by_key[key])
    if extra_headers:
        start = len(H2ActionHandler.excel_columns) + 1
        for offset, (header, value) in enumerate(extra_headers):
            sheet.cell(row=1, column=start + offset, value=header)
            sheet.cell(row=data_row, column=start + offset, value=value)

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
        certifhy = GenericCertificateFactory.create(
            certificate_id="CHY-001",
            certificate_type=GenericCertificate.CERTIFHY,
        )
        GenericCertificateFactory.create(
            certificate_id="ISCC-001",
            certificate_type=GenericCertificate.ISCC,
        )

        file_handle = build_action_import_template(H2ActionHandler(), entity)
        workbook = load_workbook(filename=BytesIO(file_handle.read()))
        file_handle.close()
        self.addCleanup(workbook.close)

        headers = [cell.value for cell in workbook["Import actions H2"][1]]
        references = workbook["References"]

        self.assertEqual(headers, [column["header"] for column in H2ActionHandler.excel_columns])

        def reference_value(key, row=2):
            index = next(i for i, spec in enumerate(H2ActionHandler.excel_columns, start=1) if spec.get("key") == key)
            return references.cell(row=row, column=index).value

        self.assertEqual(reference_value("material"), hydrogen.name)
        self.assertIsNone(reference_value("material", row=3))
        self.assertEqual(reference_value("site"), station.name)
        self.assertIsNone(reference_value("site", row=3))
        self.assertEqual(reference_value("certificate"), certifhy.certificate_id)
        self.assertIsNone(reference_value("certificate", row=3))


class ParseActionImportFileTest(TestCase):
    def test_maps_headers_to_keys_and_ignores_unknown_columns(self):
        buffer = filled_h2_template(
            pos_id="H2-001",
            material_name="Hydrogène gazeux",
            site_name="Station Paris",
            extra_headers=[("Colonne inconnue", "valeur ignorée")],
        )

        rows = parse_action_import_file(buffer, H2ActionHandler())

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["pos_id"], "H2-001")
        self.assertEqual(rows[0]["lot_id"], "LOT-001")
        self.assertEqual(rows[0]["producer"], "Air Liquide")
        self.assertEqual(rows[0]["batch_id"], "BATCH-001")
        self.assertEqual(rows[0]["material"], "Hydrogène gazeux")
        self.assertNotIn("Colonne inconnue", rows[0])
