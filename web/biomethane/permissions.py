from core.models import Entity, UserRights
from core.permissions import HasUserRights


def get_biomethane_permissions(write_actions, action):
    if not isinstance(write_actions, list):
        raise ValueError("write_actions must be a list")

    if action in write_actions:
        return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
    return [HasUserRights(entity_type=[Entity.BIOMETHANE_PRODUCER])]
