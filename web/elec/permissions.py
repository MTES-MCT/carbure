from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasCpoRights = UserRightsFactory(entity_type=[Entity.CPO])
HasElecOperatorRights = UserRightsFactory(entity_type=[Entity.OPERATOR], check=lambda entity: entity.has_elec)

HasCpoWriteRights = UserRightsFactory(
    entity_type=[Entity.CPO],
    role=[UserRights.ADMIN, UserRights.RW],
)

HasElecOperatorWriteRights = UserRightsFactory(
    entity_type=[Entity.OPERATOR],
    role=[UserRights.ADMIN, UserRights.RW],
    check=lambda entity: entity.has_elec,
)

HasElecTransferAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.TRANSFERRED_ELEC])
HasElecAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.ELEC])
