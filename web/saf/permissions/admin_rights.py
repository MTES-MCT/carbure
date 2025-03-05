from rest_framework.permissions import BasePermission

from core.common import ErrorResponse
from core.models import Entity, ExternalAdminRights, UserRights


class AdminRightsError:
    MISSING_ENTITY_ID = "MISSING_ENTITY_ID"
    USER_NOT_AUTHENTICATED = "USER_NOT_AUTHENTICATED"
    USER_NOT_VERIFIED = "USER_NOT_VERIFIED"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    ENTITY_HAS_NO_RIGHT = "ENTITY_HAS_NO_RIGHT"
    ENTITY_NOT_ADMIN = "ENTITY_NOT_ADMIN"
    USER_NOT_ADMIN = "USER_NOT_ADMIN"
    USER_HAS_NO_RIGHT = "USER_HAS_NO_RIGHT"


class HasAdminRights(BasePermission):
    """
    A permission class that checks if a user has the necessary admin rights,
    with support for dynamic parameters like `allow_external` and `allow_role`.
    """

    def __init__(self, allow_external=None, allow_role=None):
        self.allow_external = allow_external or []
        self.allow_role = allow_role

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        # Check if the user is verified
        if not request.user.is_verified():
            return False

        # Get entity_id from request
        entity_id = request.POST.get("entity_id", request.GET.get("entity_id"))
        if not entity_id:
            return False

        # Fetch the entity
        try:
            entity = Entity.objects.get(
                id=entity_id,
                entity_type__in=[Entity.ADMIN, Entity.EXTERNAL_ADMIN],
            )
        except Entity.DoesNotExist:
            return False

        # Check if the user has rights to the entity
        try:
            if self.allow_role:
                UserRights.objects.get(entity=entity, user=request.user, role__in=self.allow_role)
            else:
                UserRights.objects.get(entity=entity, user=request.user)
        except UserRights.DoesNotExist:
            return False

        # Check if the endpoint is admin-only
        is_admin_only = len(self.allow_external) == 0

        if is_admin_only:
            if entity.entity_type != Entity.ADMIN:
                return False
            if not request.user.is_staff:
                return False
        elif entity.entity_type == Entity.EXTERNAL_ADMIN:
            try:
                ExternalAdminRights.objects.get(entity=entity, right__in=self.allow_external)
            except ExternalAdminRights.DoesNotExist:
                return False

        # Store the entity and context for use in the view
        request.context = {"entity_id": entity_id, "entity": entity}
        return True

    @staticmethod
    def error_response(status_code, error_message):
        """
        Helper method to return a structured error response.
        """
        return ErrorResponse(status_code, error_message)
