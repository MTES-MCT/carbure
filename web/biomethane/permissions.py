from biomethane.services.ademe import AdemeService
from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import AdminRightsFactory, HasAdminRights, UserRightsFactory


class HasExternalAdminDepartmentsRights(HasAdminRights):
    external_right = None
    """
    Permission for external admin departments with department-based access control.
    Verifies that the user has access to the production unit's department.
    READ access only.
    """

    def __init__(self):
        super().__init__(allow_external=[self.external_right], allow_role=None)

    def has_object_permission(self, request, view, obj):
        """
        Verifies that the object (production unit or related object) belongs to an accessible department.
        """
        if obj is None:
            return False

        entity = request.entity

        if entity.entity_type != Entity.EXTERNAL_ADMIN:
            return False

        # Get accessible departments
        accessible_dept_codes = entity.get_accessible_departments().values_list("code_dept", flat=True)

        # Get the department - either directly or via production_unit property
        obj_dept = None
        if hasattr(obj, "department"):  # BiomethaneProductionUnit
            obj_dept = obj.department
        elif hasattr(obj, "production_unit"):  # All other biomethane models with @property
            production_unit = obj.production_unit
            if production_unit:
                obj_dept = production_unit.department

        return obj_dept and obj_dept.code_dept in accessible_dept_codes


class HasDrealRights(HasExternalAdminDepartmentsRights):
    external_right = ExternalAdminRights.DREAL
    """
    Permission for DREAL with department-based access control.
    Verifies that the user has access to the production unit's department.
    READ access only.
    """


class HasAdemeRights(HasExternalAdminDepartmentsRights):
    external_right = ExternalAdminRights.ADEME
    """
    Permission for ADEME with department-based access control.
    Verifies that the user has access to the production unit's department.
    Also checks that the external admin is accessing contracts with ademe investment aids.
    READ access only.
    """

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        return AdemeService.is_allowed_to_access_object(obj)


# Permission READ access for biomethane producers
HasBiomethaneProducerRights = UserRightsFactory(entity_type=[Entity.BIOMETHANE_PRODUCER])

# Permission WRITE access for biomethane producers
HasBiomethaneProducerWriteRights = UserRightsFactory(
    entity_type=[Entity.BIOMETHANE_PRODUCER],
    role=[UserRights.ADMIN, UserRights.RW],
)

# Combined permission for DREAL (READ access)
HasDrealOrAdminRights = HasDrealRights | UserRightsFactory(
    role=[UserRights.ADMIN],
)

# Combined permission for READ access for biomethane producers, DREAL and ADEME
ReadAccessBiomethane = HasBiomethaneProducerRights | HasDrealRights | HasAdemeRights

# Custom permissions to access specific endpoints

## Permission to access contract with restricted serializer fields
HasRestrictedAccessContract = AdminRightsFactory(
    allow_external=[ExternalAdminRights.ADEME],
)

## Permission to access injection site endpoint
CanAccessInjection = HasBiomethaneProducerRights | HasDrealRights

## Permission to access admin endpoints
CanAccessAdminModule = HasDrealRights | HasAdemeRights


def get_biomethane_permissions(write_actions, action):
    if not isinstance(write_actions, list):
        raise ValueError("write_actions must be a list")

    if action in write_actions:
        if action == "partial_update":
            return [(HasBiomethaneProducerWriteRights | HasDrealRights)()]
        return [HasBiomethaneProducerWriteRights()]
    return [ReadAccessBiomethane()]


def is_entity_related_to_biomethane_external_admin(entity):
    return entity.entity_type == Entity.EXTERNAL_ADMIN and (
        entity.has_external_admin_right(ExternalAdminRights.DREAL)
        or entity.has_external_admin_right(ExternalAdminRights.ADEME)
    )
