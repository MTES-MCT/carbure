from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import UserRights
from core.permissions import HasAdminRights
from core.utils import CustomPageNumberPagination
from entity.filters.admin_users import AdminUserFilter
from entity.serializers.admin_users import AdminUserIdsSerializer, AdminUserRowSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class AdminUsersViewSet(ListModelMixin, GenericViewSet):
    queryset = (
        UserRights.objects.filter(user__is_staff=False, user__is_superuser=False)
        .select_related("user", "entity")
        .order_by("user__email", "entity__name")
    )
    serializer_class = AdminUserRowSerializer
    permission_classes = [HasAdminRights]
    filterset_class = AdminUserFilter
    search_fields = ["user__email", "entity__name"]
    pagination_class = CustomPageNumberPagination

    @extend_schema(
        request=AdminUserIdsSerializer,
        responses={200: AdminUserRowSerializer(many=True)},
        filters=True,
    )
    @action(detail=False, methods=["post"], url_path="search")
    def search(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
