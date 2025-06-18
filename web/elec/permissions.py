from core.models import Entity, ExternalAdminRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasCpoUserRights = UserRightsFactory(entity_type=[Entity.CPO])
HasElecAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.ELEC])
HasElecOperatorUserRights = UserRightsFactory(entity_type=[Entity.OPERATOR], check=lambda entity: entity.has_elec)
