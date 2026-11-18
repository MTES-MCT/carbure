from django.test import TestCase

from core.factories.sample_data import ADMIN_EMAIL, USER_EMAIL, setup_france
from core.models import Entity, UserRights
from solid_biomass.factories import EnergyInstallationFactory
from solid_biomass.factories.sample_data import create_sample_data
from solid_biomass.models import EnergyInstallation
from transactions.models import Site


class EnergyInstallationFactoryTests(TestCase):
    def test_factory_creates_valid_installation_for_its_producer(self):
        setup_france()
        installation = EnergyInstallationFactory()

        installation.full_clean()
        self.assertEqual(installation.producer.entity_type, Entity.SOLID_BIOMASS_ENERGY_PRODUCER)
        self.assertEqual(installation.created_by, installation.producer)
        self.assertEqual(installation.site_type, Site.ENERGY_INSTALLATION)

    def test_sample_data_can_be_created_twice(self):
        create_sample_data()
        create_sample_data()

        installation = EnergyInstallation.objects.get(producer__name="Producteur de chaleur et d'électricité Test")
        self.assertEqual(installation.name, "Installation biomasse Test")
        self.assertEqual(EnergyInstallation.objects.count(), 1)
        self.assertTrue(
            UserRights.objects.filter(user__email=ADMIN_EMAIL, entity=installation.producer, role="ADMIN").exists()
        )
        self.assertTrue(UserRights.objects.filter(user__email=USER_EMAIL, entity=installation.producer, role="RO").exists())
