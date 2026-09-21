from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import Entity
from core.models.certificate import GenericCertificate
from core.tests_utils import setup_current_user
from h2.factories.h2_station import H2StationFactory
from h2.handlers import H2ActionHandler
from h2.serializers.action import H2ActionExcelImportSerializer
from h2.tests.excel import filled_h2_template
from traceability.factories import MaterialFactory
from traceability.models import Action
from traceability.services.action_excel import parse_action_import_file
from transactions.factories.certificate import GenericCertificateFactory
from transactions.models.site import Site


class H2ActionExcelImportViewTest(APITestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])
        self.url = reverse("traceability-action-import-actions")
        self.material = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        self.station = H2StationFactory.create(created_by=self.entity)
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

    def test_import_sums_etd1_and_etd2(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.station.name,
                certificate_id=self.certificate.certificate_id,
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Action.objects.get(pos_id="H2-001").etd, Decimal("2.000"))

    def test_import_rejects_missing_h2_extra_fields(self):
        for field in ("lot_id", "lot_quantity", "producer", "consumed_on_production_site", "etd2"):
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

    def test_import_rejects_invalid_consumed_on_production_site(self):
        response = self._post(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.station.name,
                certificate_id=self.certificate.certificate_id,
                consumed_on_production_site="Peut-être",
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Action.objects.count(), 0)
        self.assertTrue(any("consumed_on_production_site" in row["errors"] for row in response.data["validation_errors"]))

    def test_import_requires_shipping_when_not_consumed_on_production_site(self):
        for field in ("shipping_method", "shipping_distance", "shipping_date", "etd1"):
            with self.subTest(field=field):
                response = self._post(
                    filled_h2_template(
                        pos_id="H2-001",
                        material_name=self.material.name,
                        site_name=self.station.name,
                        certificate_id=self.certificate.certificate_id,
                        **{field: None},
                    )
                )

                self.assertEqual(response.status_code, 400)
                self.assertEqual(Action.objects.count(), 0)
                self.assertTrue(any(field in row["errors"] for row in response.data["validation_errors"]))

    def test_import_allows_blank_shipping_when_consumed_on_production_site(self):
        rows = parse_action_import_file(
            filled_h2_template(
                pos_id="H2-001",
                material_name=self.material.name,
                site_name=self.station.name,
                certificate_id=self.certificate.certificate_id,
                consumed_on_production_site="Oui",
                shipping_method=None,
                shipping_distance=None,
                shipping_date=None,
                etd1=None,
            ),
            H2ActionHandler(),
        )
        serializer = H2ActionExcelImportSerializer(
            data=rows,
            many=True,
            context={"handler": H2ActionHandler(), "entity": self.entity},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

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
