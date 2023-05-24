from django.urls import path
from .users import get_entity_rights
from .grant_access import accept_user
from .revoke_access import revoke_user
from .change_role import change_user_role


urlpatterns = [
    path("", get_entity_rights, name="entity-users"),
    path("grant-access", accept_user, name="entity-users-grant-access"),
    path("revoke-access", revoke_user, name="entity-users-revoke-access"),
    path("change-role", change_user_role, name="entity-users-change-role"),
]
