from datetime import date
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from core.models import Entity
from core.models.certificate import GenericCertificate
from core.tests_utils import assert_object_contains_data, setup_current_user
from h2.factories.h2_station import H2StationFactory
from h2.handlers import H2ActionHandler
from traceability.factories import MaterialFactory
from traceability.models import Action
from traceability.models.action_status import ActionStatus
from traceability.services.action_excel import build_action_import_template
from traceability.tests.services.test_action_excel import filled_h2_template
from traceability.views.mixins.excel_import import ExcelImportActionMixinErrors
from transactions.factories.certificate import GenericCertificateFactory
from transactions.models.site import Site


class ActionExcelImportViewTest(APITestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])
        self.url = reverse("traceability-action-import-actions")
        self.material = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        self.station = H2StationFactory.create(
            created_by=self.entity,
        )
        self.non_h2_station = Site.objects.create(
            name="EFS",
            site_type=Site.EFS,
            created_by=self.entity,
        )
        self.certificate = GenericCertificateFactory.create(
            certificate_id="CHY-001",
            certificate_type=GenericCertificate.CERTIFHY,
        )
        self.non_h2_certificate = GenericCertificateFactory.create(
            certificate_id="ISCC-001",
            certificate_type=GenericCertificate.ISCC,
        )

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
        file_handle = build_action_import_template(H2ActionHandler())
        buffer = BytesIO(file_handle.read())
        file_handle.close()

        response = self._post(buffer)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertEqual(response.data, {"error": ExcelImportActionMixinErrors.EMPTY_FILE})

    def test_import_creates_an_init_action_for_the_entity(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.station.name,
                certificate_id=self.certificate.certificate_id,
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["rows_imported"], 1)

        action = Action.objects.get(pos_id="H2-001")
        assert_object_contains_data(
            self,
            action,
            {
                "holder": self.entity,
                "industry": Action.H2,
                "type": Action.INIT,
                "material": self.material,
                "certificate": self.certificate,
                "site_id": self.station.id,
                "shipping_method": Action.ROAD,
                "shipping_date": date(2026, 1, 15),
                "working_date": timezone.now().date(),
                "status": ActionStatus.CREATED,
            },
        )

    def test_import_accepts_shipping_date_as_day_month_year(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.station.name,
                certificate_id=self.certificate.certificate_id,
                shipping_date="15/01/2026",
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Action.objects.get(pos_id="H2-001").shipping_date, date(2026, 1, 15))

    def test_import_rejects_unknown_material(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name="Bois",
                site_name=self.station.name,
                certificate_id=self.certificate.certificate_id,
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertTrue(response.data["validation_errors"])

    def test_import_rejects_material_from_another_industry(self):
        MaterialFactory(code="BIO-WOOD", name="Bois")

        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name="Bois",
                site_name=self.station.name,
                certificate_id=self.certificate.certificate_id,
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertTrue(response.data["validation_errors"])

    def test_import_rejects_site_from_another_industry(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.non_h2_station.name,
                certificate_id=self.certificate.certificate_id,
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertTrue(response.data["validation_errors"])

    def test_import_rejects_unknown_certificate(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.station.name,
                certificate_id="UNKNOWN-CERT",
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertTrue(response.data["validation_errors"])

    def test_import_rejects_missing_h2_extra_fields(self):
        for field in ("lot_id", "producer", "batch_id"):
            with self.subTest(field=field):
                response = self._post(
                    filled_h2_template(
                        pos_id="H2-001",
                        material_name=self.material.name,
                        site_name=self.station.name,
                        certificate_id=self.certificate.certificate_id,
                        **{field: ""},
                    )
                )

                self.assertEqual(response.status_code, 400)
                self.assertEqual(Action.objects.count(), 0)
                self.assertTrue(any(field in row["errors"] for row in response.data["validation_errors"]))

    def test_import_rejects_certificate_from_another_scheme(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.station.name,
                certificate_id=self.non_h2_certificate.certificate_id,
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertTrue(response.data["validation_errors"])
