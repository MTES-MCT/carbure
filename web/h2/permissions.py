from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasHRSRights = UserRightsFactory(entity_type=[Entity.HRS])

HasHRSWriteRights = UserRightsFactory(
    entity_type=[Entity.HRS],
    role=[UserRights.ADMIN, UserRights.RW],
)

HasH2AdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.H2])
