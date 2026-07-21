from unittest.mock import patch

from django.test import TestCase

from core.models import Pays
from entity.services.geolocation import build_site_address, resolve_gps_coordinates, site_address_changed
from transactions.factories.depot import DepotFactory
from transactions.factories.production_site import ProductionSiteFactory


class GeolocationServiceTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.france = Pays.objects.get(code_pays="FR")

    def test_build_site_address_returns_none_when_all_parts_empty(self):
        depot = DepotFactory.build(address="", postal_code="", city="", country=None)
        self.assertIsNone(build_site_address(depot))

    def test_build_site_address_returns_none_when_only_country_is_set(self):
        depot = DepotFactory.build(address="", postal_code="", city="", country=self.france)
        self.assertIsNone(build_site_address(depot))

    def test_build_site_address_joins_address_parts(self):
        depot = DepotFactory.build(
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        self.assertEqual(build_site_address(depot), "1 rue de Rivoli 75001 Paris France")

    @patch("entity.services.geolocation.get_coordinates")
    def test_resolve_gps_coordinates(self, mock_get_coordinates):
        mock_get_coordinates.return_value = (48.8566, 2.3522)
        depot = DepotFactory.build(
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        address = build_site_address(depot)
        self.assertEqual(resolve_gps_coordinates(address), "48.8566,2.3522")

    def test_site_address_changed_detects_updates(self):
        depot = DepotFactory.build(city="Paris", country=self.france)
        previous_values = {
            "address": depot.address,
            "postal_code": depot.postal_code,
            "city": "Lyon",
            "country_id": depot.country_id,
        }
        self.assertTrue(site_address_changed(depot, previous_values))


class SiteGpsInvalidationTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.france = Pays.objects.get(code_pays="FR")

    def test_site_create_does_not_set_gps_coordinates(self):
        depot = DepotFactory.create(
            gps_coordinates=None,
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        self.assertIsNone(depot.gps_coordinates)

    def test_site_create_keeps_provided_gps_coordinates(self):
        depot = DepotFactory.create(
            gps_coordinates="48.8566,2.3522",
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        self.assertEqual(depot.gps_coordinates, "48.8566,2.3522")

    def test_site_update_clears_gps_when_address_changes(self):
        depot = DepotFactory.create(
            gps_coordinates="48.8566,2.3522",
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )

        depot.city = "Lyon"
        depot.save()

        self.assertIsNone(depot.gps_coordinates)

    def test_site_update_keeps_gps_when_address_unchanged(self):
        depot = DepotFactory.create(
            gps_coordinates="48.8566,2.3522",
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )

        depot.name = "Updated depot name"
        depot.save()

        self.assertEqual(depot.gps_coordinates, "48.8566,2.3522")

    def test_production_site_update_clears_gps_when_address_changes(self):
        production_site = ProductionSiteFactory.create(
            gps_coordinates="48.8566,2.3522",
            address="10 avenue de France",
            postal_code="75013",
            city="Paris",
            country=self.france,
        )

        production_site.city = "Lyon"
        production_site.save()

        self.assertIsNone(production_site.gps_coordinates)
