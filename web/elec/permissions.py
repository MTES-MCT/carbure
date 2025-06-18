from core.models import Entity, ExternalAdminRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasCpoUserRights = UserRightsFactory(entity_type=[Entity.CPO])
HasElecOperatorUserRights = UserRightsFactory(entity_type=[Entity.OPERATOR], check=lambda entity: entity.has_elec)
HasElecTransferAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.TRANSFERRED_ELEC])
HasElecAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.ELEC])
