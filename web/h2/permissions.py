from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasHRSRights = UserRightsFactory(entity_type=[Entity.HRS])

HasHRSWriteRights = UserRightsFactory(
    entity_type=[Entity.HRS],
    role=[UserRights.ADMIN, UserRights.RW],
)


def is_tiruert_liable(entity):
    return entity.is_tiruert_liable


HasTiruertLiableRights = UserRightsFactory(check=is_tiruert_liable)

HasTiruertLiableWriteRights = UserRightsFactory(
    role=[UserRights.ADMIN, UserRights.RW],
    check=is_tiruert_liable,
)

HasH2AdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.H2])
