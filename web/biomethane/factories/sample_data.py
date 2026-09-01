from biomethane.factories.contract import create_contract_with_amendments
from biomethane.factories.energy import create_biomethane_energy
from biomethane.factories.injection_site import create_injection_site
from biomethane.factories.production_unit import create_production_unit
from biomethane.factories.supply_plan import create_supply_plan
from core.factories.sample_data import set_user_access, setup_admin_user, setup_regular_user
from core.models import Entity
from entity.factories.entity import EntityFactory


def create_sample_data():
    admin_user = setup_admin_user()
    regular_user = setup_regular_user()

    entity = EntityFactory.create(
        name="Producteur de biométhane Test",
        entity_type=Entity.BIOMETHANE_PRODUCER,
    )

    set_user_access(admin_user, entity, "ADMIN")
    set_user_access(regular_user, entity, "RO")

    create_contract_with_amendments(entity)
    create_production_unit(entity)
    create_injection_site(entity)
    create_biomethane_energy(entity)
    create_supply_plan(entity)
