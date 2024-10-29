from django.db.models import Q
from core.models import Entity


def get_administrated_entities(admin_entity: Entity):
    if admin_entity.entity_type not in [Entity.ADMIN, Entity.EXTERNAL_ADMIN]:
        raise Exception("Entity is not admin")

    administrated_entities = Entity.objects.all()

    # limit entities for DGAC
    if admin_entity.has_external_admin_right("AIRLINE"):
        administrated_entities = administrated_entities.filter(entity_type=Entity.AIRLINE)

    # limit entities for Elec stuff
    if admin_entity.has_external_admin_right("ELEC"):
        administrated_entities = administrated_entities.filter(Q(entity_type=Entity.CPO) | Q(entity_type=Entity.OPERATOR, has_elec=True))

    return administrated_entities
