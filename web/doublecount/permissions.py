from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasProducerRights = UserRightsFactory(entity_type=[Entity.PRODUCER])
HasDoubleCountingAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])

HasProducerWriteRights = UserRightsFactory(
    entity_type=[Entity.PRODUCER],
    role=[UserRights.ADMIN, UserRights.RW],
)

HasDoubleCountingAdminWriteRights = AdminRightsFactory(
    allow_external=[ExternalAdminRights.DOUBLE_COUNTING],
    allow_role=[UserRights.ADMIN, UserRights.RW],
)
