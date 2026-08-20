from core.models import Entity
from core.seeds.users import get_admin_user, get_regular_user, set_user_access
from entity.factories.entity import EntityFactory

HRS_ENTITY_NAME = "Distributeur H2"


def setup_hrs_entity():
    hrs_entity = EntityFactory(
        name=HRS_ENTITY_NAME,
        entity_type=Entity.HRS,
    )

    set_user_access(get_admin_user(), hrs_entity, "ADMIN")
    set_user_access(get_regular_user(), hrs_entity, "RW")


def get_hrs_entity():
    return Entity.objects.get(name=HRS_ENTITY_NAME, entity_type=Entity.HRS)
