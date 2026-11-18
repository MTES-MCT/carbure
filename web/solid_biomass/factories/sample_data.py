from datetime import date

from core.factories.sample_data import set_user_access, setup_admin_user, setup_france, setup_regular_user
from core.models import Entity
from entity.factories.entity import EntityFactory
from solid_biomass.factories import EnergyInstallationFactory
from solid_biomass.models import EnergyInstallation


def setup_producer() -> Entity:
    producer = EntityFactory(
        name="Producteur de chaleur et d'électricité Test",
        entity_type=Entity.SOLID_BIOMASS_ENERGY_PRODUCER,
    )
    set_user_access(setup_admin_user(), producer, "ADMIN")
    set_user_access(setup_regular_user(), producer, "RO")
    return producer


def setup_energy_installation(producer: Entity) -> EnergyInstallation:
    return EnergyInstallationFactory(
        producer=producer,
        name="Installation biomasse Test",
        site_siret="12345678900012",
        address="1 rue de la Biomasse",
        postal_code="75001",
        city="Paris",
        country=setup_france(),
        private=False,
        production_type=EnergyInstallation.COGENERATION,
        commissioning_date=date(2020, 1, 1),
    )


def create_sample_data():
    producer = setup_producer()
    setup_energy_installation(producer)
