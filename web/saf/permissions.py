from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasSafOperatorRights = UserRightsFactory(entity_type=[Entity.OPERATOR], check=lambda entity: entity.has_saf)
HasSafTraderRights = UserRightsFactory(entity_type=[Entity.SAF_TRADER])
HasAirlineRights = UserRightsFactory(entity_type=[Entity.AIRLINE])

HasSafOperatorWriteRights = UserRightsFactory(
    entity_type=[Entity.OPERATOR],
    role=[UserRights.ADMIN, UserRights.RW],
    check=lambda entity: entity.has_saf,
)

HasSafTraderWriteRights = UserRightsFactory(
    entity_type=[Entity.SAF_TRADER],
    role=[UserRights.ADMIN, UserRights.RW],
)

HasAirlineWriteRights = UserRightsFactory(
    entity_type=[Entity.AIRLINE],
    role=[UserRights.ADMIN, UserRights.RW],
)

HasSafAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.AIRLINE])
