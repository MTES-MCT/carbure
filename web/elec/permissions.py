from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory


def has_elec_liable_rights(entity):
    return entity.is_tiruert_liable and entity.has_elec


HasCpoRights = UserRightsFactory(entity_type=[Entity.CPO])
HasElecOperatorRights = UserRightsFactory(check=has_elec_liable_rights)

HasCpoWriteRights = UserRightsFactory(
    entity_type=[Entity.CPO],
    role=[UserRights.ADMIN, UserRights.RW],
)

HasElecOperatorWriteRights = UserRightsFactory(
    role=[UserRights.ADMIN, UserRights.RW],
    check=has_elec_liable_rights,
)

HasElecTransferAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.TRANSFERRED_ELEC])
HasElecAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.ELEC])
