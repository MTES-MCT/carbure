from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.factories import MaterialFactory
from traceability.models import Action
from transactions.models import Site


class ActionExcelTemplateViewTest(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])
        self.url = reverse("traceability-action-download-import-template")

    def test_download_returns_excel_with_h2_headers_and_lookup_options(self):
        hydrogen = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        MaterialFactory(code="BIO-WOOD", name="Bois")
        station = Site.objects.create(name="Station Paris", site_type=Site.H2_REFUELING_STATION)
        Site.objects.create(name="Dépôt Lyon", site_type=Site.EFS)

        response = self.client.get(self.url, {"entity_id": self.entity.id, "industry": Action.H2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.ms-excel")

        workbook = load_workbook(filename=BytesIO(response.content))
        self.addCleanup(workbook.close)
        headers = [cell.value for cell in workbook["Import actions H2"][1]]
        references = workbook["References"]

        self.assertEqual(headers[0], "N° de POS")
        self.assertEqual(headers[1], "Nature d'hydrogène")
        self.assertEqual(headers[2], "Quantité (MJ)")
        self.assertEqual(headers[3], "Station")
        self.assertEqual(references["B2"].value, hydrogen.name)
        self.assertEqual(references["D2"].value, station.name)
