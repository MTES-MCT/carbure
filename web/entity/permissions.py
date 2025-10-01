from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])
HasProducerRights = UserRightsFactory(entity_type=[Entity.PRODUCER])
HasProducerWriteRights = UserRightsFactory(entity_type=[Entity.PRODUCER], role=[UserRights.RW, UserRights.ADMIN])
