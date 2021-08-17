from rest_framework import permissions
from core.models import UserRights

class ReadPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_verified():
            return False

        entity_id = request.query_params.get('entity_id')
        if not entity_id:
            return False

        has_right = UserRights.objects.filter(user=request.user, entity_id=entity_id).exists()
        return has_right


class ReadWritePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_verified():
            return False

        entity_id = request.query_params.get('entity_id')
        if not entity_id:
            return False

        has_right = UserRights.objects.get(user=request.user, entity_id=entity_id, role__in=[UserRights.RW, UserRights.ADMIN]).exists()
        return has_right