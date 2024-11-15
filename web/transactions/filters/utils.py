from core.models import Entity


def is_admin_user(request, entity_id):
    if entity_id is None:
        return False

    try:
        # check that entity exists and is admin
        entity = Entity.objects.get(id=entity_id, entity_type__in=[Entity.ADMIN])
    except Exception:
        return False

    # confirm that the current entity is the administration
    if entity.entity_type != Entity.ADMIN:
        return False
    # and confirm that the current user is part of the staff
    if not request.user.is_staff:
        return False

    return True


def is_auditor_user(entity_id):
    try:
        entity = Entity.objects.get(id=entity_id, entity_type__in=[Entity.AUDITOR])
    except Exception:
        return False

    if entity.entity_type != Entity.AUDITOR:
        return False

    return True
