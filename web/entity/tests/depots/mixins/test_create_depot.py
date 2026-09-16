from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity, Pays
from core.tests_utils import setup_current_user
from entity.factories.entity import EntityFactory
from transactions.models import Depot, EntitySite


class TestCreateDepot(TestCase):
    fixtures = ["json/countries.json"]

    @classmethod
    def setUpTestData(cls):
        cls.country = Pays.objects.get(code_pays="FR")
        cls.entity = EntityFactory.create(entity_type=Entity.OPERATOR, name="Authorized operator")
        cls.other_entity = EntityFactory.create(entity_type=Entity.OPERATOR, name="Other operator")

    def setUp(self):
        setup_current_user(
            self,
            email="tester@carbure.local",
            name="Tester",
            password="gogogo",
            entity_rights=[(self.entity, "RW")],
        )

    def create_depot(self, entity_id, data, **kwargs):
        url = reverse("api-entity-depots-create-depot")
        return self.client.post(url, data, query_params={"entity_id": entity_id}, **kwargs)

    def valid_payload(self, **overrides):
        payload = {
            "name": "Dépôt de test",
            "city": "Paris",
            "country_code": self.country.code_pays,
            "depot_type": Depot.BIOFUELDEPOT,
            "depot_id": "123456789012345",
            "ownership_type": EntitySite.OWN,
        }
        payload.update(overrides)
        return payload

    def test_create_depot_success(self):
        payload = self.valid_payload()

        response = self.create_depot(self.entity.pk, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        depot = Depot.objects.get(customs_id=payload["depot_id"])
        entity_site = EntitySite.objects.get(site=depot)

        self.assertEqual(depot.name, payload["name"])
        self.assertFalse(depot.is_enabled)
        self.assertEqual(depot.created_by, self.entity)
        self.assertEqual(entity_site.entity, self.entity)

    def test_create_depot_requires_depot_id(self):
        payload = self.valid_payload()
        payload.pop("depot_id")

        response = self.create_depot(self.entity.pk, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("depot_id", response.json())

    def test_create_depot_ignores_forged_entity_id_and_system_fields(self):
        payload = self.valid_payload(
            entity_id=self.other_entity.pk,
            created_by=self.other_entity.pk,
            is_enabled=True,
            gps_coordinates="48.8566,2.3522",
            private=True,
        )

        response = self.create_depot(self.entity.pk, payload, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        depot = Depot.objects.get(customs_id=payload["depot_id"])
        entity_site = EntitySite.objects.get(site=depot)

        self.assertEqual(depot.created_by, self.entity)
        self.assertEqual(entity_site.entity, self.entity)
        self.assertFalse(depot.is_enabled)
        self.assertIsNone(depot.gps_coordinates)
        self.assertFalse(depot.private)
