from core.models import Entity, ExternalAdminRights
from core.permissions import AdminRightsFactory, UserRightsFactory

HasCpoUserRights = UserRightsFactory(entity_type=[Entity.CPO])
HasElecAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.ELEC])
