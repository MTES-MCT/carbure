# test with : python web/manage.py test elec.api.admin.audit.meter_readings.tests_audit_meter_readings.ElecAdminAuditMeterReadingsTest --keepdb

import datetime
import stat
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse
from elec.api.cpo import charge_points

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

        charge_point = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="ABCDE",
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
        )

        meter_readings_application = ElecMeterReadingApplication.objects.create(cpo=self.cpo, quarter=1, year=2023)

        meter_reading = ElecMeterReading.objects.create(
            extracted_energy=1234,
            renewable_energy=2345,
            reading_date=datetime.date(2023, 6, 29),
            charge_point=charge_point,
            application=meter_readings_application,
            cpo=self.cpo,
        )
        return meter_readings_application, meter_reading

    def test_accept_application(self):
        application, meter_reading = self.create_application()
        self.assertEqual(application.status, ElecChargePointApplication.PENDING)

        # force accept without audit
        response = self.client.post(
            reverse("elec-admin-audit-meter-readings-accept-application"),
            {
                "application_id": application.id,
                "entity_id": self.admin.id,
                "force_validation": "true",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

        application.refresh_from_db()
        self.assertEqual(application.status, ElecChargePointApplication.ACCEPTED)

        # provision certificate should have been created
        # certificate = ElecProvisionCertificate.objects.get(cpo=self.cpo, quarter=1, year=2023)
        # self.assertEqual(certificate.energy_amount, 1000.1234)
