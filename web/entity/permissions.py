from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])
HasProducerRights = UserRightsFactory(entity_type=[Entity.PRODUCER])
HasProducerWriteRights = UserRightsFactory(entity_type=[Entity.PRODUCER], role=[UserRights.RW, UserRights.ADMIN])
HasOperatorRights = UserRightsFactory(entity_type=[Entity.OPERATOR])
HasOperatorWriteRights = UserRightsFactory(entity_type=[Entity.OPERATOR], role=[UserRights.RW, UserRights.ADMIN])
HasDgddiWriteRights = AdminRightsFactory(
    allow_external=[ExternalAdminRights.DGDDI], allow_role=[UserRights.RW, UserRights.ADMIN]
)


def check_if_red_ii_for_biomethane(entity: Entity):
    return entity.entity_type != Entity.BIOMETHANE_PRODUCER or entity.is_red_ii


HasCertificateRights = UserRightsFactory(
    entity_type=[Entity.PRODUCER, Entity.TRADER, Entity.OPERATOR, Entity.POWER_OR_HEAT_PRODUCER, Entity.BIOMETHANE_PRODUCER],
    check=check_if_red_ii_for_biomethane,
)

HasCertificateWriteRights = UserRightsFactory(
    entity_type=[Entity.PRODUCER, Entity.TRADER, Entity.OPERATOR, Entity.POWER_OR_HEAT_PRODUCER, Entity.BIOMETHANE_PRODUCER],
    role=[UserRights.RW, UserRights.ADMIN],
    check=check_if_red_ii_for_biomethane,
)

HasCertificateAdminRights = AdminRightsFactory(
    allow_external=[ExternalAdminRights.DOUBLE_COUNTING, ExternalAdminRights.TRANSFERRED_ELEC]
)

HasCertificateAdminWriteRights = AdminRightsFactory(
    allow_external=[ExternalAdminRights.DOUBLE_COUNTING, ExternalAdminRights.TRANSFERRED_ELEC],
    allow_role=[UserRights.RW, UserRights.ADMIN],
)
