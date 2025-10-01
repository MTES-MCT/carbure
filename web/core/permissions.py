from types import FunctionType
from typing import Callable, Literal, Optional

from rest_framework.permissions import BasePermission

from core.common import ErrorResponse
from core.models import Entity, ExternalAdminRights, UserRights

# Admin rights


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
        if not request.user.is_authenticated:
            return False

        if not request.user.is_verified():
            return False

        entity = request.entity
        if not entity:
            return False

        # Check if the user has rights to the entity
        try:
            if self.allow_role:
                UserRights.objects.get(entity=entity, user=request.user, role__in=self.allow_role)
            else:
                UserRights.objects.get(entity=entity, user=request.user)
        except UserRights.DoesNotExist:
            return False

        # Check if the user is staff to access admin entities
        if entity.entity_type == Entity.ADMIN:
            if not request.user.is_staff:
                return False
        # Otherwise check if the external admin right is allowed
        elif entity.entity_type == Entity.EXTERNAL_ADMIN:
            try:
                ExternalAdminRights.objects.get(entity=entity, right__in=self.allow_external)
            except ExternalAdminRights.DoesNotExist:
                return False
        # If we're not on an admin-type entity, forbid access
        else:
            return False

        # Store the entity and context for use in the view
        request.context = {"entity_id": entity.id, "entity": entity}
        return True

    @staticmethod
    def error_response(status_code, error_message):
        """
        Helper method to return a structured error response.
        """
        return ErrorResponse(status_code, error_message)


# User rights


class HasUserRights(BasePermission):
    role = None
    entity_type = None

    def __init__(self, role=None, entity_type=None, check=None):
        super().__init__()
        self.role = role
        self.entity_type = entity_type
        self.check = check

    def __call__(self):
        return self

    def has_permission(self, request, view):
        user = request.user
        if not user or user.is_anonymous:
            return False

        if not request.user.is_verified():
            return False

        entity = request.entity
        if entity is None:
            return False

        if isinstance(self.entity_type, list) and entity.entity_type not in self.entity_type:
            return False

        if isinstance(self.check, FunctionType):
            if not self.check(entity):
                return False

        rights = {str(ur.entity_id): ur.role for ur in UserRights.objects.filter(user=request.user)}

        request.session["rights"] = rights

        entity_id = str(entity.id)

        if entity_id not in rights:
            return False

        if entity_id != request.session.get("entity_id"):
            request.session["entity_id"] = entity_id

        user_role = rights[entity_id]
        if isinstance(self.role, list) and user_role not in self.role:
            return False
        return True


# static types

EntityType = Literal[
    "Producteur",
    "Opérateur",
    "Trader",
    "Administration",
    "Auditor",
    "Administration Externe",
    "Compagnie aérienne",
    "Unknown",
    "Charge Point Operator",
    "Power or Heat Producer",
]

UserRole = Literal[
    "RO",
    "RW",
    "ADMIN",
    "AUDITOR",
]

ExternalAdmin = Literal[
    "AIRLINE",
    "DCA",
    "AGRIMER",
    "TIRIB",
    "ELEC",
    "TRANSFERRED_ELEC",
]


def AdminRightsFactory(allow_external: Optional[list[ExternalAdmin]] = None, allow_role: Optional[list[UserRole]] = None):
    class _HasAdminRights(HasAdminRights):
        def __init__(self):
            super().__init__(allow_external, allow_role)

    return _HasAdminRights


def UserRightsFactory(
    role: Optional[list[UserRole]] = None,
    entity_type: Optional[list[EntityType]] = None,
    check: Optional[Callable[[Entity], bool]] = None,
):
    class _HasUserRights(HasUserRights):
        def __init__(self):
            super().__init__(role, entity_type, check)

    return _HasUserRights
