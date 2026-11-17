from core.models import Entity, ExternalAdminRights


def is_hrs_holder(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return actor.entity_type == Entity.HRS and holder == actor


def can_hrs_transfer(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return actor.entity_type == Entity.HRS and parent_holder == actor and holder.is_tiruert_liable


def is_h2_admin(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return actor.entity_type == Entity.ADMIN or actor.has_external_admin_right(ExternalAdminRights.H2)
