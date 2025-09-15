from core.models import Entity, UserRights
from core.permissions import HasUserRights


class BiomethanePermissionsMixin:
    # Actions qui nécessitent des droits d'écriture
    write_actions = []

    def get_permissions(self):
        if self.action in self.write_actions:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return [HasUserRights(entity_type=self.BIOMETHANE_ENTITY_TYPE)]
