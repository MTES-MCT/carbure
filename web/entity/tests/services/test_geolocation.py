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
        mock_get_coordinates.return_value = (2.3522, 48.8566)
        depot = DepotFactory.build(
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        self.assertEqual(resolve_gps_coordinates(depot), "2.3522,48.8566")

    def test_site_address_changed_detects_updates(self):
        depot = DepotFactory.build(city="Paris", country=self.france)
        previous_values = {
            "address": depot.address,
            "postal_code": depot.postal_code,
            "city": "Lyon",
            "country_id": depot.country_id,
        }
        self.assertTrue(site_address_changed(depot, previous_values))


class SiteGeolocationSaveTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.france = Pays.objects.get(code_pays="FR")

    @patch("entity.services.geolocation.get_coordinates")
    def test_site_create_fills_gps_coordinates(self, mock_get_coordinates):
        mock_get_coordinates.return_value = (2.3522, 48.8566)
        depot = DepotFactory.create(
            gps_coordinates=None,
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        self.assertEqual(depot.gps_coordinates, "2.3522,48.8566")

    @patch("entity.services.geolocation.get_coordinates")
    def test_site_create_keeps_provided_gps_coordinates(self, mock_get_coordinates):
        depot = DepotFactory.create(
            gps_coordinates="1.0,2.0",
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        mock_get_coordinates.assert_not_called()
        self.assertEqual(depot.gps_coordinates, "1.0,2.0")

    @patch("entity.services.geolocation.get_coordinates")
    def test_site_update_regenerates_gps_when_address_changes(self, mock_get_coordinates):
        mock_get_coordinates.return_value = (2.3522, 48.8566)
        depot = DepotFactory.create(
            gps_coordinates="1.0,2.0",
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        mock_get_coordinates.reset_mock()
        mock_get_coordinates.return_value = (4.8357, 45.7640)

        depot.city = "Lyon"
        depot.save()

        self.assertEqual(depot.gps_coordinates, "4.8357,45.764")
        mock_get_coordinates.assert_called_once()

    @patch("entity.services.geolocation.get_coordinates")
    def test_site_update_keeps_gps_when_address_unchanged(self, mock_get_coordinates):
        depot = DepotFactory.create(
            gps_coordinates="1.0,2.0",
            address="1 rue de Rivoli",
            postal_code="75001",
            city="Paris",
            country=self.france,
        )
        mock_get_coordinates.reset_mock()

        depot.name = "Updated depot name"
        depot.save()

        self.assertEqual(depot.gps_coordinates, "1.0,2.0")
        mock_get_coordinates.assert_not_called()

    @patch("entity.services.geolocation.get_coordinates")
    def test_production_site_create_fills_gps_coordinates(self, mock_get_coordinates):
        mock_get_coordinates.return_value = (2.3522, 48.8566)
        production_site = ProductionSiteFactory.create(
            gps_coordinates=None,
            address="10 avenue de France",
            postal_code="75013",
            city="Paris",
            country=self.france,
        )
        self.assertEqual(production_site.gps_coordinates, "2.3522,48.8566")
