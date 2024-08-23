# test with : python web/manage.py test elec.api.admin.audit.meter_readings.tests_audit_meter_readings.ElecAdminAuditMeterReadingsTest.test_accept_application --keepdb

import datetime
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.models import Entity, UserRights
from core.tests_utils import setup_current_user
from elec.models.elec_audit_charge_point import ElecAuditChargePoint
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.import_elec_audit_report_excel import import_elec_audit_report_excel


class ElecAdminAuditMeterReadingsTest(TestCase):
    def setUp(self):
        self.auditor = Entity.objects.create(
            name="Auditor",
            entity_type=Entity.AUDITOR,
            has_elec=True,
        )

        self.cpo = Entity.objects.create(
            name="CPO",
            entity_type=Entity.CPO,
            has_elec=True,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.cpo, UserRights.AUDITOR), (self.auditor, UserRights.ADMIN)],
        )

    def create_audit_samples(self):
        charge_point_application = ElecChargePointApplication.objects.create(cpo=self.cpo)

        charge_point_1 = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="ABCD01",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="ABCD",
            nominal_power=150,
            cpo_name="",
            cpo_siren="",
            latitude=48.7566,
            longitude=2.2522,
        )

        charge_point_2 = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="ABCD02",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 12),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="ABCD",
            nominal_power=150,
            cpo_name="",
            cpo_siren="",
            latitude=48.8566,
            longitude=2.3522,
        )

        charge_point_3 = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="ABCD03",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 12),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="ABCD",
            nominal_power=150,
            cpo_name="",
            cpo_siren="",
            latitude=48.9566,
            longitude=2.4522,
        )

        charge_point_audit_sample = ElecAuditSample.objects.create(
            cpo=self.cpo,
            percentage=1,
            charge_point_application=charge_point_application,
        )

        charge_point_audit_1 = ElecAuditChargePoint.objects.create(
            audit_sample=charge_point_audit_sample,
            charge_point=charge_point_1,
        )

        charge_point_audit_2 = ElecAuditChargePoint.objects.create(
            audit_sample=charge_point_audit_sample,
            charge_point=charge_point_2,
        )

        charge_point_audit_3 = ElecAuditChargePoint.objects.create(
            audit_sample=charge_point_audit_sample,
            charge_point=charge_point_3,
        )

        meter_reading_application = ElecMeterReadingApplication.objects.create(cpo=self.cpo, quarter=3, year=2023)

        meter_reading_1 = ElecMeterReading.objects.create(
            extracted_energy=1234,
            renewable_energy=2345,
            reading_date=datetime.date(2023, 8, 29),
            charge_point=charge_point_1,
            application=meter_reading_application,
            cpo=self.cpo,
        )

        meter_reading_2 = ElecMeterReading.objects.create(
            extracted_energy=8900,
            renewable_energy=2000,
            reading_date=datetime.date(2023, 9, 1),
            charge_point=charge_point_2,
            application=meter_reading_application,
            cpo=self.cpo,
        )

        meter_reading_3 = ElecMeterReading.objects.create(
            extracted_energy=10900,
            renewable_energy=2400,
            reading_date=datetime.date(2023, 9, 1),
            charge_point=charge_point_2,
            application=meter_reading_application,
            cpo=self.cpo,
        )

        meter_reading_audit_sample = ElecAuditSample.objects.create(
            cpo=self.cpo,
            percentage=1,
            meter_reading_application=meter_reading_application,
        )

        meter_reading_audit_1 = ElecAuditChargePoint.objects.create(
            audit_sample=meter_reading_audit_sample,
            meter_reading=meter_reading_1,
            charge_point=charge_point_1,
        )

        meter_reading_audit_2 = ElecAuditChargePoint.objects.create(
            audit_sample=meter_reading_audit_sample,
            meter_reading=meter_reading_2,
            charge_point=charge_point_2,
        )

        meter_reading_audit_3 = ElecAuditChargePoint.objects.create(
            audit_sample=meter_reading_audit_sample,
            meter_reading=meter_reading_3,
            charge_point=charge_point_3,
        )

        return charge_point_audit_sample, meter_reading_audit_sample

    def test_import_charge_point_audit_report_excel(self):
        # 48.7566	2.2522	ABCD	ABCD01	[MID] 123-456	[MID] 123-456	OUI	OUI	AC	1/6/24	1000,1234
        # 48.8566	2.3522	ABCD	ABCD02	[MID] 123-456	[MID] 123-457	OUI	NON	CC	2/6/24	1002
        # 48.9566	2.4522	ABCD	ABCD03	[MID] 123-456							                        CHARGE POINT NOT FOUND
        filepath = f"{os.environ['CARBURE_HOME']}/web/elec/fixtures/charge_point_audit_sample.xlsx"
        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("charge_point_audit_sample.xlsx", reader.read())

        charge_point_audit_sample, _ = self.create_audit_samples()
        audited_charge_points = charge_point_audit_sample.audited_charge_points.all()
        charge_point_audits, errors = import_elec_audit_report_excel(file, audited_charge_points)

        self.assertEqual(len(charge_point_audits), 3)
        self.assertEqual(len(errors), 0)

        self.assertDictEqual(
            charge_point_audits[0],
            {
                "charge_point_id": "ABCD01",
                "observed_mid_or_prm_id": "[MID] 123-456",
                "is_auditable": True,
                "has_dedicated_pdl": True,
                "current_type": "AC",
                "audit_date": datetime.date(2024, 6, 1),
                "observed_energy_reading": 1000.1234,
                "comment": "",
            },
        )

        self.assertDictEqual(
            charge_point_audits[1],
            {
                "charge_point_id": "ABCD02",
                "observed_mid_or_prm_id": "[MID] 123-457",
                "is_auditable": True,
                "has_dedicated_pdl": False,
                "current_type": "DC",
                "audit_date": datetime.date(2024, 6, 2),
                "observed_energy_reading": 1002,
                "comment": "",
            },
        )

        self.assertDictEqual(
            charge_point_audits[2],
            {
                "charge_point_id": "ABCD03",
                "observed_mid_or_prm_id": "",
                "is_auditable": False,
                "has_dedicated_pdl": False,
                "current_type": "",
                "audit_date": None,
                "observed_energy_reading": 0,
                "comment": "Charge point was not found",
            },
        )

    def test_check_report(self):
        charge_point_audit_sample, _ = self.create_audit_samples()

        with open(f"{os.environ['CARBURE_HOME']}/web/elec/fixtures/charge_point_audit_sample.xlsx", "rb") as reader:
            file = SimpleUploadedFile("charge_point_audit_sample.xlsx", reader.read())

        # force accept without audit
        response = self.client.post(
            reverse("elec-auditor-check-report"),
            {
                "file": file,
                "audit_sample_id": charge_point_audit_sample.pk,
                "entity_id": self.auditor.pk,
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_accept_report(self):
        _, meter_reading_audit_sample = self.create_audit_samples()

        with open(f"{os.environ['CARBURE_HOME']}/web/elec/fixtures/meter_reading_audit_sample.xlsx", "rb") as reader:
            file = SimpleUploadedFile("meter_reading_audit_sample.xlsx", reader.read())

        # force accept without audit
        response = self.client.post(
            reverse("elec-auditor-accept-report"),
            {
                "file": file,
                "audit_sample_id": meter_reading_audit_sample.pk,
                "entity_id": self.auditor.pk,
            },
        )

        charge_points_audited = meter_reading_audit_sample.audited_charge_points.select_related("charge_point").all()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(charge_points_audited[0].is_auditable, True)
        self.assertEqual(charge_points_audited[0].current_type, "AC")
        self.assertEqual(charge_points_audited[0].observed_mid_or_prm_id, "[MID] 123-456")
        self.assertEqual(charge_points_audited[0].observed_energy_reading, 1234)
        self.assertEqual(charge_points_audited[0].has_dedicated_pdl, True)
        self.assertEqual(charge_points_audited[0].audit_date, datetime.date(2024, 6, 1))
        self.assertEqual(charge_points_audited[0].comment, "")

        self.assertEqual(charge_points_audited[1].is_auditable, True)
        self.assertEqual(charge_points_audited[1].current_type, "DC")
        self.assertEqual(charge_points_audited[1].observed_mid_or_prm_id, "[MID] 123-457")
        self.assertEqual(charge_points_audited[1].observed_energy_reading, 8900)
        self.assertEqual(charge_points_audited[1].has_dedicated_pdl, False)
        self.assertEqual(charge_points_audited[1].audit_date, datetime.date(2024, 6, 2))
        self.assertEqual(charge_points_audited[1].comment, "")

        self.assertEqual(charge_points_audited[2].is_auditable, False)
        self.assertEqual(charge_points_audited[2].current_type, "")
        self.assertEqual(charge_points_audited[2].observed_mid_or_prm_id, "")
        self.assertEqual(charge_points_audited[2].observed_energy_reading, 0)
        self.assertEqual(charge_points_audited[2].has_dedicated_pdl, False)
        self.assertEqual(charge_points_audited[2].audit_date, None)
        self.assertEqual(charge_points_audited[2].comment, "Charge point was not found")
