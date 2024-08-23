# test with : python web/manage.py test elec.api.admin.audit.meter_readings.tests_audit_meter_readings.ElecAdminAuditMeterReadingsTest.test_accept_application --keepdb

import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.models.elec_provision_certificate import ElecProvisionCertificate


class ElecAdminAuditMeterReadingsTest(TestCase):
    def setUp(self):
        self.admin = Entity.objects.create(
            name="Admin",
            entity_type=Entity.ADMIN,
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
            [(self.cpo, "RW"), (self.admin, "ADMIN")],
        )

    def create_application(self):
        charge_point_application = ElecChargePointApplication.objects.create(cpo=self.cpo)

        charge_point1 = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="ABCDE12345",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=150,
            cpo_name="",
            cpo_siren="",
            latitude=48.8566,
            longitude=2.3522,
        )

        charge_point2 = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="FGX10398",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 12),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=150,
            cpo_name="",
            cpo_siren="",
            latitude=48.9566,
            longitude=2.1522,
        )

        meter_readings_application = ElecMeterReadingApplication.objects.create(cpo=self.cpo, quarter=3, year=2023)

        meter_reading1 = ElecMeterReading.objects.create(
            extracted_energy=1234,
            renewable_energy=2345,
            reading_date=datetime.date(2023, 8, 29),
            charge_point=charge_point1,
            application=meter_readings_application,
            cpo=self.cpo,
        )

        meter_reading2 = ElecMeterReading.objects.create(
            extracted_energy=8900,
            renewable_energy=2000,
            reading_date=datetime.date(2023, 9, 1),
            charge_point=charge_point1,
            application=meter_readings_application,
            cpo=self.cpo,
        )

        meter_reading3 = ElecMeterReading.objects.create(
            extracted_energy=8900,
            renewable_energy=2000,
            reading_date=datetime.date(2023, 9, 1),
            charge_point=charge_point2,
            application=meter_readings_application,
            cpo=self.cpo,
        )
        return meter_readings_application, [meter_reading1, meter_reading2, meter_reading3]

    def test_accept_application(self):
        application, meter_readings = self.create_application()
        assert application.status == ElecChargePointApplication.PENDING

        # create sample
        assert application.audit_sample.first() is None
        response = self.client.post(
            reverse("elec-admin-audit-meter-readings-generate-sample"),
            {
                "application_id": application.id,
                "entity_id": self.admin.id,
                "percentage": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["charge_points"]) == 1
        assert application.status == ElecChargePointApplication.PENDING
        audit_sample = application.audit_sample.first()
        assert audit_sample is not None
        assert audit_sample.status == ElecAuditSample.IN_PROGRESS

        # force accept without audit
        response = self.client.post(
            reverse("elec-admin-audit-meter-readings-accept-application"),
            {
                "application_id": application.id,
                "entity_id": self.admin.id,
                "force_validation": "true",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"status": "success"}

        application.refresh_from_db()
        assert application.status == ElecChargePointApplication.ACCEPTED

        # audit_sample should be marked as audited
        audit_sample.refresh_from_db()
        assert audit_sample.status == ElecAuditSample.AUDITED

        # provision certificate should have been created
        certificates = ElecProvisionCertificate.objects.filter(cpo=self.cpo, quarter=3, year=2023)
        assert len(certificates) == 2
        assert (
            certificates.first().energy_amount
            == (meter_readings[0].renewable_energy + meter_readings[1].renewable_energy) / 1000
        )
        assert certificates[1].energy_amount == meter_readings[2].renewable_energy / 1000
