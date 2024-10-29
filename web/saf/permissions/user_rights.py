from rest_framework.permissions import BasePermission

from core.models import Entity, ExternalAdminRights, UserRights


class BaseEntityPermission(BasePermission):
    def get_entity(self, request):
        entity_id = request.POST.get("entity_id", request.GET.get("entity_id"))
        if not entity_id:
            return None

        try:
            entity = Entity.objects.get(pk=entity_id)
        except Entity.DoesNotExist:
            return None

        return entity

    def get_user_rights(self, request, entity):
        try:
            rights = UserRights.objects.get(entity=entity, user=request.user)
        except UserRights.DoesNotExist:
            return None
        return rights


class IsVerifiedUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified()


class HasUserRights(BaseEntityPermission):
    role = None
    entity_type = None

    def __init__(self, role=None, entity_type=None):
        super().__init__()
        self.role = role
        self.entity_type = entity_type

    def __call__(self):
        return self

    def has_permission(self, request, view):
        if not request.user.is_verified():
            return False
        entity = self.get_entity(request)
        if entity is None:
            return False

        rights = {str(ur.entity_id): ur.role for ur in UserRights.objects.filter(user=request.user)}

        request.session["rights"] = rights

        entity_id = str(entity.id)

        if entity_id not in rights:
            return False

        if entity_id != request.session.get("entity_id"):
            request.session["entity_id"] = entity_id

        user_role = rights[entity_id]
        if isinstance(self.entity_type, list) and entity.entity_type not in self.entity_type:
            return False

        if isinstance(self.role, list) and user_role not in self.role:
            return False
        return True


class HasAdminRights(BaseEntityPermission):
    allow_external = None
    role = None

    def __init__(self, allow_external=None, role=None):
        super().__init__()
        self.role = role
        self.allow_external = allow_external

    def has_permission(self, request, view):
        entity = self.get_entity(request)
        if entity is None or entity.entity_type not in [
            Entity.ADMIN,
            Entity.EXTERNAL_ADMIN,
        ]:
            return False

        rights = self.get_user_rights(request, entity)
        if rights is None:
            return False

        allow_external = self.allow_external if isinstance(self.allow_external, list) else []
        is_admin_only = len(self.allow_external) == 0

        if is_admin_only:
            if entity.entity_type != Entity.ADMIN or not request.user.is_staff:
                return False
        elif entity.entity_type == Entity.EXTERNAL_ADMIN:
            try:
                ExternalAdminRights.objects.get(entity=entity, right__in=allow_external)
            except ExternalAdminRights.DoesNotExist:
                return False

