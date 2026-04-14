from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

TIRUERT_ENTITIES = [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER]


def can_access_balance_and_operations(entity):
    requires_mac = entity.entity_type in [Entity.TRADER, Entity.PRODUCER]
    return (not requires_mac or entity.has_mac) and entity.accise_number != ""


def can_access_objectives(entity):
    requires_mac = entity.entity_type in [Entity.TRADER, Entity.PRODUCER]
    return (not requires_mac or entity.has_mac) and entity.accise_number != "" and entity.is_tiruert_liable


HasTiruertRightsBalanceAndOperations = UserRightsFactory(
    entity_type=TIRUERT_ENTITIES, check=can_access_balance_and_operations
)

TiruertAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.TIRIB_STATS])
TiruertUserRights = UserRightsFactory(entity_type=TIRUERT_ENTITIES, check=can_access_objectives)
HasTiruertRightsObjectives = TiruertUserRights | TiruertAdminRights

HasTiruertWriteRights = UserRightsFactory(entity_type=TIRUERT_ENTITIES, role=[UserRights.RW, UserRights.ADMIN])
