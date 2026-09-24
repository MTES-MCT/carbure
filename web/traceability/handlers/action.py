from django.db.models import Q

import traceability.handlers.lookups as default_lookups
from core.permissions import HasEntityReadRights, HasEntityWriteRights
from traceability.handlers.excel import ACTION_EXCEL_COLUMNS, excel_column
from traceability.serializers.action import ActionExcelImportSerializer


class ActionIndustryHandler:
    """Per-industry plugin loaded from the `industry` query param."""

    industry: str | None = None
    lookups = default_lookups
    excel_columns: list[dict] = [excel_column(key) for key in ACTION_EXCEL_COLUMNS]
    excel_import_serializer_class = ActionExcelImportSerializer
    write_actions = ("destroy", "import_actions")
    read_permission = HasEntityReadRights
    write_permission = HasEntityWriteRights
    admin_permission = None

    @classmethod
    def get_permissions(cls, action: str):
        if action in cls.write_actions:
            return [cls.write_permission()]
        permission = cls.read_permission
        if cls.admin_permission is not None:
            permission = permission | cls.admin_permission
        return [permission()]

    @classmethod
    def scope_queryset(cls, request, queryset):
        queryset = queryset.filter(industry=cls.industry)
        if cls._is_industry_admin(request):
            return queryset
        return queryset.filter(Q(holder=request.entity) | Q(parent__holder=request.entity))

    @classmethod
    def _is_industry_admin(cls, request):
        if cls.admin_permission is None:
            return False
        return cls.admin_permission().has_permission(request, None)
