import json

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from entity.factories.entity import EntityFactory
from solid_biomass.models import EnergyInstallation
from solid_biomass.serializers.energy_installation import EnergyInstallationSerializer
from transactions.models import Site


class EnergyInstallationTests(TestCase):
    def setUp(self):
        self.producer = EntityFactory.create(entity_type=Entity.SOLID_BIOMASS_ENERGY_PRODUCER)
        self.other = EntityFactory.create(entity_type=Entity.PRODUCER)
        self.user = setup_current_user(
            self,
            email="installation@example.com",
            name="Tester",
            password="password",
            entity_rights=[(self.producer, "RW"), (self.other, "RW")],
        )
        self.url = reverse("energy-installation")

    def test_url_is_in_solid_biomass_api(self):
        self.assertEqual(self.url, "/api/solid-biomass/energy-installation/")

    def put_installation(self, entity, data):
        return self.client.put(
            self.url, data=json.dumps(data), content_type="application/json", query_params={"entity_id": entity.id}
        )

    def test_create_update_and_clear_conditional_fields(self):
        response = self.put_installation(
            self.producer,
            {
                "production_type": "COGENERATION",
                "heat_type": "STEAM",
                "useful_temperature": 150,
                "electrical_efficiency": 40,
                "commissioning_date": "2025-09-25",
            },
        )
        self.assertEqual(response.status_code, 200)
        installation = EnergyInstallation.objects.get(producer=self.producer)
        self.assertEqual(installation.site_type, Site.ENERGY_INSTALLATION)
        self.assertEqual(installation.created_by, self.producer)
        response = self.put_installation(self.producer, {"icpe_number": "0123456789", "icpe_regime": "AUTHORIZATION"})
        self.assertEqual(response.status_code, 200)
        response = self.put_installation(self.producer, {"production_type": "ELECTRICITY", "electrical_efficiency": None})
        self.assertEqual(response.status_code, 200)
        installation.refresh_from_db()
        self.assertIsNone(installation.heat_type)
        self.assertIsNone(installation.useful_temperature)
        self.assertIsNone(installation.electrical_efficiency)
        self.assertEqual(installation.icpe_number, "0123456789")
        self.assertEqual(EnergyInstallation.objects.count(), 1)

    def test_validation_and_entity_type(self):
        self.assertEqual(self.put_installation(self.producer, {"icpe_number": "123"}).status_code, 400)
        self.assertEqual(self.put_installation(self.producer, {"thermal_efficiency": 101}).status_code, 400)
        self.assertEqual(self.put_installation(self.other, {}).status_code, 403)
        self.assertEqual(self.client.get(self.url, query_params={"entity_id": self.other.id}).status_code, 403)


class EnergyInstallationSerializerTests(SimpleTestCase):
    def test_efficiencies_follow_production_type(self):
        for production_type, electrical, thermal in [
            (EnergyInstallation.ELECTRICITY, 40, None),
            (EnergyInstallation.HEAT, None, 80),
            (EnergyInstallation.COGENERATION, 40, 80),
            (None, None, None),
        ]:
            with self.subTest(production_type=production_type):
                instance = EnergyInstallation(
                    production_type=EnergyInstallation.COGENERATION,
                    electrical_efficiency=40,
                    thermal_efficiency=80,
                )
                serializer = EnergyInstallationSerializer(
                    instance,
                    data={"production_type": production_type, "electrical_efficiency": 40, "thermal_efficiency": 80},
                    partial=True,
                )
                self.assertTrue(serializer.is_valid(), serializer.errors)
                self.assertEqual(serializer.validated_data["electrical_efficiency"], electrical)
                self.assertEqual(serializer.validated_data["thermal_efficiency"], thermal)

    def test_changing_production_type_clears_conditional_values(self):
        instance = EnergyInstallation(production_type="COGENERATION", heat_type="STEAM", useful_temperature=150)
        serializer = EnergyInstallationSerializer(instance, data={"production_type": "ELECTRICITY"}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.validated_data["heat_type"])
        self.assertIsNone(serializer.validated_data["useful_temperature"])

    def test_clearing_production_type_clears_heat_type(self):
        instance = EnergyInstallation(production_type="HEAT", heat_type="STEAM")
        serializer = EnergyInstallationSerializer(instance, data={"production_type": None}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.validated_data["heat_type"])

    def test_invalid_icpe_and_efficiency(self):
        serializer = EnergyInstallationSerializer(data={"icpe_number": "123", "electrical_efficiency": 101}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("icpe_number", serializer.errors)
        self.assertIn("electrical_efficiency", serializer.errors)
