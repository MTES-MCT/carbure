from core.models import Entity, UserRights
from core.permissions import UserRightsFactory

HasHRSRights = UserRightsFactory(entity_type=[Entity.HRS])

HasHRSWriteRights = UserRightsFactory(
    entity_type=[Entity.HRS],
    role=[UserRights.ADMIN, UserRights.RW],
)
