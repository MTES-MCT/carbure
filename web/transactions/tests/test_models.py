from django.core.exceptions import ValidationError
from django.test import TestCase

from transactions.factories.depot import DepotFactory
from transactions.factories.production_site import ProductionSiteFactory


class TestDepotModels(TestCase):
    fixtures = [
        "json/countries.json",
    ]

    def test_some_fields_are_cleared_when_creating_depot_with_power_plant_type(self):
        depot = DepotFactory.build(site_type="POWER PLANT")

        assert depot.thermal_efficiency is None
        assert depot.useful_temperature is None

    def test_some_fields_are_cleared_when_creating_depot_with_heat_plant_type(self):
        depot = DepotFactory.build(site_type="HEAT PLANT")

        assert depot.electrical_efficiency is None
        assert depot.useful_temperature is None

    def test_some_fields_are_cleared_when_creating_depot_with_cogeneration_plant_type(self):
        depot = DepotFactory.build(site_type="COGENERATION PLANT")

        assert depot.electrical_efficiency is None
        assert depot.thermal_efficiency is None

    def test_clean_raises_error_when_customs_id_is_missing(self):
        """Test que la fonction clean lève une erreur quand customs_id n'est pas fourni"""
        depot = DepotFactory.build(customs_id=None)

        with self.assertRaises(ValidationError) as context:
            depot.clean()

        # Vérifier que l'erreur contient le bon message pour customs_id
        self.assertIn("customs_id", context.exception.error_dict)

    def test_clean_raises_error_when_customs_id_is_already_used(self):
        """Test que la fonction clean lève une erreur quand customs_id est déjà utilisé"""
        DepotFactory.create(customs_id="123456789012345")

        depot2 = DepotFactory.build(customs_id="123456789012345")
        with self.assertRaises(ValidationError) as context:
            depot2.clean()

        self.assertIn("customs_id", context.exception.error_dict)

    def test_clean_raises_error_when_name_is_already_used(self):
        """Test que la fonction clean lève une erreur quand name est déjà utilisé"""
        DepotFactory.create(name="Dépôt de test")

        depot2 = DepotFactory.build(name="Dépôt de test")
        with self.assertRaises(ValidationError) as context:
            depot2.clean()

        self.assertIn("name", context.exception.error_dict)


class TestProductionSiteModels(TestCase):
    fixtures = [
        "json/countries.json",
    ]

    def test_clean_raises_error_when_date_mise_en_service_is_missing(self):
        """Test que la fonction clean lève une erreur quand date_mise_en_service est manquant"""
        production_site = ProductionSiteFactory.build(date_mise_en_service=None)

        with self.assertRaises(ValidationError) as context:
            production_site.clean()

        self.assertIn("date_mise_en_service", context.exception.error_dict)
