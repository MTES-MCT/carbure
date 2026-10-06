import os
import tempfile
from datetime import datetime

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from core.excel import ExcelResponse, export_to_excel
from core.filters import FiltersActionFactory
from core.models import UserRights
from core.permissions import HasAdminRights
from core.utils import CustomPageNumberPagination
from entity.filters.admin_users import AdminUserFilter
from entity.serializers.admin_users import AdminEntityIdsSerializer, AdminUserRowSerializer


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
class AdminUsersViewSet(FiltersActionFactory(), ListModelMixin, GenericViewSet):
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

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.request.method != "POST":
            return queryset

        serializer = AdminEntityIdsSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        entity_ids = serializer.validated_data.get("entity_ids")
        if entity_ids is not None:
            queryset = queryset.filter(entity_id__in=entity_ids)
        return queryset

    @extend_schema(
        request=AdminEntityIdsSerializer,
        responses={200: AdminUserRowSerializer(many=True)},
        filters=True,
    )
    @action(detail=False, methods=["post"], url_path="search")
    def search(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        request=AdminEntityIdsSerializer,
        filters=True,
        responses={(200, "application/vnd.ms-excel"): OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=["post"], url_path="export")
    def export(self, request, *args, **kwargs):
        rows = self.filter_queryset(self.get_queryset())
        filename = f"carbure_utilisateurs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        excel_file = export_to_excel(
            os.path.join(tempfile.gettempdir(), filename),
            [
                {
                    "label": "Utilisateurs",
                    "rows": rows,
                    "columns": [
                        {"label": "Entité", "value": "entity.name"},
                        {"label": "Type d'entité", "value": lambda row: row.entity.get_entity_type_display()},
                        {"label": "Entity id", "value": "entity_id"},
                        {"label": "Utilisateur", "value": "user.email"},
                        {"label": "Rôle", "value": lambda row: row.get_role_display()},
                        {"label": "Actif", "value": lambda row: "Oui" if row.user.is_active else "Non"},
                    ],
                }
            ],
            column_width=28,
        )
        return ExcelResponse(excel_file)
