from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.handlers.h2 import H2ActionHandler
from traceability.models import Action
from traceability.services.action_excel import resolve_action_excel_columns


class ActionExcelTemplateViewTest(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])
        self.url = reverse("traceability-action-download-import-template")

    def test_download_returns_excel_with_h2_headers(self):
        response = self.client.get(self.url, {"entity_id": self.entity.id, "industry": Action.H2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.ms-excel")

        workbook = load_workbook(filename=BytesIO(response.content))
        self.addCleanup(workbook.close)
        sheet = workbook["Import actions H2"]
        expected_headers = [column.label for column in resolve_action_excel_columns(H2ActionHandler())]

        self.assertEqual([cell.value for cell in sheet[1]], expected_headers)
