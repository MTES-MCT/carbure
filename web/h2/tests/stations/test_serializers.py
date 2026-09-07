from django.test import TestCase

from core.models import Entity, Pays
from h2.models import H2Station
from h2.serializers import H2StationInputSerializer


class H2StationInputSerializerTests(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(name="Test HRS", entity_type=Entity.HRS)
        self.country = Pays.objects.create(code_pays="FR", name="France", name_en="France")

    def _payload(self, **overrides):
        data = {
            "name": "Station H2 Test",
            "address": "1 rue de la Pompe",
            "postal_code": "75001",
            "city": "Paris",
            "country": self.country.pk,
            "access_type": H2Station.PUBLIC,
            "distributed_pressure": [H2Station.DP_350_BAR],
            "has_personal_vehicle_connector": True,
            "has_compliant_measuring_instruments": True,
            "storage_capacity": 1000,
            "distribution_capacity": 500,
        }
        data.update(overrides)
        return data

    def test_invalid_distributed_pressure(self):
        serializer = H2StationInputSerializer(data=self._payload(distributed_pressure=[999]))
        self.assertFalse(serializer.is_valid())
        self.assertIn("distributed_pressure", serializer.errors)

    def test_missing_distributed_pressure(self):
        payload = self._payload()
        del payload["distributed_pressure"]

        serializer = H2StationInputSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("distributed_pressure", serializer.errors)

    def test_empty_distributed_pressure(self):
        serializer = H2StationInputSerializer(data=self._payload(distributed_pressure=[]))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["distributed_pressure"], [])

    def test_compliant_measuring_instruments_defaults_to_false(self):
        payload = self._payload()
        del payload["has_compliant_measuring_instruments"]

        serializer = H2StationInputSerializer(data=payload, context={"entity": self.entity})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        station = serializer.save()
        self.assertFalse(station.has_compliant_measuring_instruments)
