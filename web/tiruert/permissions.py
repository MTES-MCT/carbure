from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

TIRUERT_ENTITIES = [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER]


def can_access_balance_and_operations(entity):
    if entity.entity_type == Entity.OPERATOR:
        return True
    if entity.entity_type in [Entity.TRADER, Entity.PRODUCER]:
        return entity.has_mac
    return False


def can_access_objectives(entity):
    return can_access_balance_and_operations(entity) and entity.is_tiruert_liable


HasTiruertRightsBalanceAndOperations = UserRightsFactory(
    entity_type=TIRUERT_ENTITIES, check=can_access_balance_and_operations
)

TiruertAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.DGDDI_NATIONAL])
TiruertUserRights = UserRightsFactory(entity_type=TIRUERT_ENTITIES, check=can_access_objectives)
HasTiruertRightsObjectives = TiruertUserRights | TiruertAdminRights

HasTiruertWriteRights = UserRightsFactory(entity_type=TIRUERT_ENTITIES, role=[UserRights.RW, UserRights.ADMIN])
