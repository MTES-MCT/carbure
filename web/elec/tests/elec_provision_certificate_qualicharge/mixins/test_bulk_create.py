from copy import deepcopy

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import Entity
from core.tests_utils import setup_current_user_with_jwt
from elec.factories import ElecProvisionCertificateQualichargeFactory
from elec.models import ElecProvisionCertificateQualicharge
from entity.factories import EntityFactory
from transactions.models import YearConfig


class BulkCreateMixinTest(TestCase):
    """Integration tests for bulk creation mixin - focuses on API integration, not business logic"""

    def setUp(self):
        # Create YearConfig for tests
        YearConfig.objects.get_or_create(year=2023, defaults={"renewable_share": 0.25})

        self.client = APIClient()
        self.cpo = EntityFactory.create(
            name="Test CPO",
            entity_type=Entity.CPO,
            has_elec=True,
            registration_id="123456789",
        )

        self.data = [
            {
                "entity": "Test CPO",
                "siren": "123456789",
                "operational_units": [
                    {
                        "code": "FR001",
                        "from": "2023-01-01",
                        "to": "2023-03-31",
                        "stations": [
                            {
                                "id": "FRXYZP123456",
                                "energy": 1000.0,
                                "is_controlled": True,
                            }
                        ],
                    }
                ],
            }
        ]

        self.user = setup_current_user_with_jwt(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.cpo, "RW")],
        )

        self.url = reverse("elec-provision-certificate-qualicharge-bulk-create")

    def test_bulk_create_success(self):
        """Test successful bulk creation through API endpoint"""
        assert self.user is not None

        response = self.client.post(
            self.url,
            data=self.data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ElecProvisionCertificateQualicharge.objects.count(), 1)

    def test_bulk_create_double_validated_error(self):
        """Test that API returns error for already double-validated certificate"""
        ElecProvisionCertificateQualichargeFactory.create(
            cpo=self.cpo,
            operating_unit="FR001",
            station_id="FRXYZP123456",
            energy_amount=500.0,
            double_validated=True,
        )

        response = self.client.post(
            self.url,
            data=self.data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertIn("errors", json_response)
        self.assertTrue(len(json_response["errors"]) > 0)

    def test_validation_errors_keep_sparse_indexes_at_every_level(self):
        data = [deepcopy(self.data[0]), deepcopy(self.data[0])]
        data[1]["entity"] = "Second CPO"
        data[1]["siren"] = "invalid"
        units = data[1]["operational_units"]
        units.append(deepcopy(units[0]))
        units[1]["code"] = "FR002"
        units[1]["from"] = "invalid"
        stations = units[1]["stations"]
        stations.append(deepcopy(stations[0]))
        stations[1]["id"] = "FRXYZP654321"
        stations[1]["energy"] = "invalid"

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, 400)
        errors = response.json()["errors"]
        self.assertEqual(len(errors), 3)
        self.assertTrue(all(error["index"] == "1" for error in errors))
        self.assertTrue(all(error["entity"] == "Second CPO" for error in errors))
        by_field = {error["field"]: error for error in errors}
        self.assertIn("siren", by_field)
        self.assertEqual(by_field["from"]["unit_code"], "FR002")
        self.assertEqual(by_field["energy"]["station_id"], "FRXYZP654321")
        self.assertEqual(ElecProvisionCertificateQualicharge.objects.count(), 0)

    def test_invalid_list_fields_return_validation_errors(self):
        for field, value in (("operational_units", None), ("operational_units", "invalid")):
            with self.subTest(value=value):
                data = deepcopy(self.data)
                data[0][field] = value
                response = self.client.post(self.url, data=data, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["errors"][0]["field"], field)
