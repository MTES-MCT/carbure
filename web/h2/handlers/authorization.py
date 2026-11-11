from core.models import Entity, ExternalAdminRights
from traceability.models import Action


def is_hrs_holder(actor: Entity, action: Action) -> bool:
    return actor.entity_type == Entity.HRS and action.holder == actor


def is_h2_admin(actor: Entity, action: Action) -> bool:
    return actor.entity_type == Entity.ADMIN or actor.has_external_admin_right(ExternalAdminRights.H2)
