import factory

from core.models import Entity
from entity.factories.entity import EntityFactory
from solid_biomass.models import EnergyInstallation
from transactions.factories.site import SiteFactory


class EnergyInstallationFactory(SiteFactory):
    class Meta:
        model = EnergyInstallation
        django_get_or_create = ("producer",)

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.SOLID_BIOMASS_ENERGY_PRODUCER)
    created_by = factory.SelfAttribute("producer")
    production_type = EnergyInstallation.COGENERATION
    heat_type = "STEAM"
    useful_temperature = 150
    electrical_efficiency = 35
    thermal_efficiency = 50
    icpe_number = "0123456789"
    icpe_regime = "AUTHORIZATION"
