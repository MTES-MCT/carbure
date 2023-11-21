import datetime
import os
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


class ElecCPOTest(TestCase):
    def setUp(self):
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
            [(self.cpo, "RW")],
        )

    def test_check_charge_point_certificate(self):
        filepath = "%s/web/fixtures/csv/test_data/points-de-recharge-inscription.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("points-de-recharge-inscription.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-check-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        expected = (
            {
                "status": "error",
                "error": "APPLICATION_FAILED",
                "data": {
                    "file_name": "points-de-recharge-inscription.xlsx",
                    "charging_point_count": 1,
                    "errors": [{"error": "MISSING_CHARGING_POINT_IN_DATAGOUV", "meta": ["ABCDEFG"]}],
                    "error_count": 1,
                },
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)
