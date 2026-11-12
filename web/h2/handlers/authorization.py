from core.models import Entity, ExternalAdminRights


def can_create_consumption(actor, parent_holder, child_holder):
    return actor.entity_type == Entity.HRS and actor == child_holder


def can_create_valorization(actor, parent_holder, child_holder):
    is_admin = actor.entity_type == Entity.ADMIN
    is_h2_admin = actor.has_external_admin_right(ExternalAdminRights.H2)
    return (is_admin or is_h2_admin) and child_holder.entity_type == Entity.HRS
