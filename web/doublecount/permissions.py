from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasProducerRights = UserRightsFactory(entity_type=[Entity.PRODUCER])
HasProducerWriteRights = UserRightsFactory(entity_type=[Entity.PRODUCER], role=[UserRights.ADMIN, UserRights.RW])
HasDoubleCountingAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])
