from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import Entity
from core.models.certificate import GenericCertificate
from core.tests_utils import assert_object_contains_data, setup_current_user
from h2.factories.h2_station import H2StationFactory
from traceability.factories import MaterialFactory
from traceability.models import Action
from traceability.models.action_status import ActionStatus
from traceability.tests.services.test_action_excel import filled_h2_template
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
                "working_date": date(2026, 1, 15),
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

    def test_import_rejects_missing_lot_id(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.station.name,
                certificate_id=self.certificate.certificate_id,
                lot_id="",
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertTrue(any("lot_id" in row["errors"] for row in response.data["validation_errors"]))

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
