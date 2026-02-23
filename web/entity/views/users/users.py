from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, viewsets

from core.models import ExternalAdminRights, UserRights
from core.permissions import HasAdminRights, HasUserRights
from entity.views.users.mixins import UserActionMixin

User = get_user_model()


class EntityUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "name", "email"]

    @extend_schema_field(serializers.CharField())
    def get_name(self, obj):
        return obj.name


class UserViewSet(UserActionMixin, viewsets.GenericViewSet):
    serializer_class = EntityUserSerializer
    pagination_class = None

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        if self.action in ["change_role", "accept_user", "invite_user", "revoke_access", "entity_rights_requests"]:
            return [HasUserRights(role=[UserRights.ADMIN])]

        if self.action in ["rights_requests"]:
            return [
                HasAdminRights(
                    allow_external=[
                        ExternalAdminRights.AIRLINE,
                        ExternalAdminRights.ELEC,
                        ExternalAdminRights.TRANSFERRED_ELEC,
                        ExternalAdminRights.DOUBLE_COUNTING,
                        ExternalAdminRights.DREAL,
                    ]
                )
            ]

        if self.action in ["update_right_request", "update_user_role"]:
            return [
                HasAdminRights(
                    allow_role=[UserRights.RW, UserRights.ADMIN],
                    allow_external=[
                        ExternalAdminRights.AIRLINE,
                        ExternalAdminRights.ELEC,
                        ExternalAdminRights.DOUBLE_COUNTING,
                        ExternalAdminRights.DREAL,
                    ],
                )
            ]

        return super().get_permissions()
