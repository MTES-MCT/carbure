from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import HasAdminRights, UserRightsFactory


class HasDrealRights(HasAdminRights):
    """
    Permission for DREAL with department-based access control.
    Verifies that the user has access to the production unit's department.
    READ access only.
    """

    def __init__(self):
        super().__init__(allow_external=[ExternalAdminRights.DREAL], allow_role=None)

    def has_object_permission(self, request, view, obj):
        """
        Verifies that the object (production unit or related object) belongs to an accessible department.
        """
        entity = request.entity

        if entity.entity_type != Entity.EXTERNAL_ADMIN:
            return False
        # Get the DREAL right for this entity
        try:
            dreal_right = ExternalAdminRights.objects.get(entity=entity, right=ExternalAdminRights.DREAL)
        except ExternalAdminRights.DoesNotExist:
            return False

        # Get accessible departments
        accessible_dept_codes = dreal_right.get_accessible_departments().values_list("code_dept", flat=True)

        # Get the department - either directly or via production_unit property
        obj_dept = None
        if hasattr(obj, "department"):  # BiomethaneProductionUnit
            obj_dept = obj.department
        elif hasattr(obj, "production_unit"):  # All other biomethane models with @property
            production_unit = obj.production_unit
            if production_unit:
                obj_dept = production_unit.department

        return obj_dept and obj_dept.code_dept in accessible_dept_codes


# Permission READ access for biomethane producers
HasBiomethaneProducerRights = UserRightsFactory(entity_type=[Entity.BIOMETHANE_PRODUCER])

# Permission WRITE access for biomethane producers
HasBiomethaneProducerWriteRights = UserRightsFactory(
    entity_type=[Entity.BIOMETHANE_PRODUCER],
    role=[UserRights.ADMIN, UserRights.RW],
)

# Combined permission for DREAL (READ access)
HasDrealOrProducerRights = HasBiomethaneProducerRights | HasDrealRights


def get_biomethane_permissions(write_actions, action):
    if not isinstance(write_actions, list):
        raise ValueError("write_actions must be a list")

    if action in write_actions:
        return [HasBiomethaneProducerWriteRights()]
    return [HasDrealOrProducerRights()]
