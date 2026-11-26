from core.models import Entity, ExternalAdminRights


def is_hrs_holder(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return actor.entity_type == Entity.HRS and holder == actor


def can_hrs_transfer(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return (
        actor.entity_type == Entity.HRS and parent_holder == actor and holder != parent_holder and holder.is_tiruert_liable
    )


def can_liable_transfer(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return bool(actor.is_tiruert_liable and parent_holder == actor and holder != parent_holder and holder.is_tiruert_liable)


def can_transfer(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return can_hrs_transfer(actor, holder, parent_holder) or can_liable_transfer(actor, holder, parent_holder)


def can_liable_consume(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return bool(actor.is_tiruert_liable and holder == actor and parent_holder == actor)


def is_liable_holder(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return actor.is_tiruert_liable and holder == actor


def is_h2_admin(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool:
    return actor.entity_type == Entity.ADMIN or actor.has_external_admin_right(ExternalAdminRights.H2)
