from datetime import date
from decimal import Decimal
from io import BytesIO
from logging import getLogger
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import Entity, StoredFile
from core.tests_utils import assert_object_contains_data, setup_current_user
from traceability.factories import MaterialFactory
from traceability.handlers.registry import ACTION_HANDLERS
from traceability.models import Action
from traceability.models.action_status import ActionStatus
from traceability.services.action_excel import build_action_import_template
from traceability.services.action_import_file import ACTION_IMPORT_UPLOAD_DIR
from traceability.tests.excel import GenericExcelHandler, filled_generic_template
from traceability.views.mixins.excel_import import ExcelImportActionMixinErrors
from transactions.factories.certificate import GenericCertificateFactory
from transactions.models import Site


class ActionExcelImportViewTest(APITestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.handler_patch = patch.dict(ACTION_HANDLERS, {Action.H2: GenericExcelHandler})
        self.handler_patch.start()
        self.addCleanup(self.handler_patch.stop)

        self.entity = Entity.objects.create(name="Opérateur", entity_type=Entity.OPERATOR)
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])
        self.url = reverse("traceability-action-import-actions")
        self.material = MaterialFactory(code="MAT-001", name="Matière")
        self.site = Site.objects.create(name="Site", site_type=Site.EFS, created_by=self.entity)
        self.certificate = GenericCertificateFactory.create(certificate_id="CERT-001")

    def _post(self, buffer):
        uploaded = SimpleUploadedFile(
            "import.xlsx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        return self.client.post(
            self.url,
            {"file": uploaded},
            query_params={"entity_id": self.entity.id, "industry": Action.H2},
            format="multipart",
        )

    def test_import_rejects_empty_file(self):
        file_handle = build_action_import_template(GenericExcelHandler())
        buffer = BytesIO(file_handle.read())
        file_handle.close()

        response = self._post(buffer)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertEqual(StoredFile.objects.count(), 0)
        self.assertEqual(response.data, {"error": ExcelImportActionMixinErrors.EMPTY_FILE})

    def test_import_creates_an_init_action_for_the_entity(self):
        response = self._post(
            filled_generic_template(
                material_name=self.material.name,
                site_name=self.site.name,
                certificate_id=self.certificate.certificate_id,
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["rows_imported"], 1)

        action = Action.objects.get(pos_id="ACT-001")
        assert_object_contains_data(
            self,
            action,
            {
                "holder": self.entity,
                "industry": Action.H2,
                "type": Action.INIT,
                "unit": Action.KG,
                "material": self.material,
                "certificate": self.certificate,
                "site_id": self.site.id,
                "shipping_method": Action.ROAD,
                "shipping_date": date(2026, 1, 15),
                "working_date": date(2026, 2, 1),
                "etd": Decimal("0.000"),
                "status": ActionStatus.PENDING,
            },
        )

        stored_file = StoredFile.objects.get()
        self.assertEqual(action.file_id, stored_file.id)
        self.assertEqual(stored_file.name, "import.xlsx")
        self.assertEqual(stored_file.entity, self.entity)
        self.assertEqual(stored_file.user, self.user)
        self.assertTrue(stored_file.url.name.startswith(f"{ACTION_IMPORT_UPLOAD_DIR}/{self.entity.id}/"))
        self.assertTrue(stored_file.url.name.endswith(".xlsx"))

    def test_import_accepts_shipping_date_as_day_month_year(self):
        response = self._post(
            filled_generic_template(
                material_name=self.material.name,
                site_name=self.site.name,
                certificate_id=self.certificate.certificate_id,
                shipping_date="15/01/2026",
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Action.objects.get(pos_id="ACT-001").shipping_date, date(2026, 1, 15))

    def test_import_accepts_working_date_as_month_year(self):
        response = self._post(
            filled_generic_template(
                material_name=self.material.name,
                site_name=self.site.name,
                certificate_id=self.certificate.certificate_id,
                working_date="02/2026",
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Action.objects.get(pos_id="ACT-001").working_date, date(2026, 2, 1))

    def test_import_accepts_blank_shipping_method(self):
        response = self._post(
            filled_generic_template(
                material_name=self.material.name,
                site_name=self.site.name,
                certificate_id=self.certificate.certificate_id,
                shipping_method=None,
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Action.objects.get(pos_id="ACT-001").shipping_method, "")

    def test_import_rejects_unknown_material(self):
        response = self._post(
            filled_generic_template(
                material_name="Inconnue",
                site_name=self.site.name,
                certificate_id=self.certificate.certificate_id,
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertEqual(StoredFile.objects.count(), 0)
        self.assertTrue(response.data["validation_errors"])

    def test_import_rejects_unknown_certificate(self):
        response = self._post(
            filled_generic_template(
                material_name=self.material.name,
                site_name=self.site.name,
                certificate_id="UNKNOWN-CERT",
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertEqual(StoredFile.objects.count(), 0)
        self.assertTrue(response.data["validation_errors"])

    def test_import_deletes_file_when_action_create_fails(self):
        with (
            patch(
                "traceability.serializers.action.Action.bulk_create",
                side_effect=RuntimeError("db down"),
            ),
            patch("django.db.models.fields.files.FieldFile.delete") as mock_delete,
            patch.object(getLogger("django.request"), "error"),
        ):
            with self.assertRaises(RuntimeError):
                self._post(
                    filled_generic_template(
                        material_name=self.material.name,
                        site_name=self.site.name,
                        certificate_id=self.certificate.certificate_id,
                    )
                )

        mock_delete.assert_called_once_with(save=False)
        self.assertEqual(Action.objects.count(), 0)
        self.assertEqual(StoredFile.objects.count(), 0)
