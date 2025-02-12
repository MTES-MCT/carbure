from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_field
from rest_framework import serializers, viewsets
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from core.models import ExternalAdminRights, UserRights
from entity.views.users.mixins import UserActionMixin
from saf.permissions import HasAdminRights, HasUserRights

User = get_user_model()


class EntityUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "name", "email"]

    @extend_schema_field(serializers.CharField())
    def get_name(self, obj):
        return obj.name


class UserViewSet(ListModelMixin, viewsets.GenericViewSet, UserActionMixin):
    serializer_class = EntityUserSerializer
    pagination_class = None
    permission_classes = [
        HasUserRights() or HasAdminRights(allow_external=[]),
    ]

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        # TODO fix permissions if needed
        if self.action in [
            "change_role",
            "accept_user",
            "invite_user",
            "revoke_access",
        ]:
            return [HasUserRights([UserRights.ADMIN], None)]

        if self.action in [
            "rights_requests",
            "update_right_request",
            "update_user_role",
        ]:
            return [
                HasAdminRights(
                    allow_external=[
                        ExternalAdminRights.AIRLINE,
                        ExternalAdminRights.ELEC,
                        ExternalAdminRights.DOUBLE_COUNTING,
                    ]
                )
            ]

        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
            OpenApiParameter(
                "company_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Compay ID, Admin only",
                required=True,
            ),
            OpenApiParameter(name="q", type=str, description="Search in user email or entity name."),
        ],
        responses=EntityUserSerializer(many=True),
    )
    def list(self, request):
        q = self.request.query_params.get("q")
        company_id = self.request.query_params.get("company_id")
        user_model = get_user_model()
        users = user_model.objects.all()

        if q:
            users = users.filter(Q(email__icontains=q) | Q(name__icontains=q))
        if company_id:
            users = users.filter(userrights__entity__id=company_id)
        users_sez = [{"email": u.email, "name": u.name, "id": u.id} for u in users]
        return Response(users_sez)
