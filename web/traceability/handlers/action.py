from collections.abc import Callable

from django.db.models import Q

import traceability.handlers.lookups as default_lookups
from core.models import Entity
from core.permissions import HasEntityReadRights, HasEntityWriteRights
from traceability.handlers.excel import ACTION_EXCEL_COLUMNS, excel_column
from traceability.models import Action
from traceability.serializers.action import ActionExcelImportSerializer
from traceability.serializers.consumption import ConsumptionSerializer

ActionFlowEdge = tuple[tuple[str, str] | None, tuple[str, str]]


class ActionIndustryHandler:
    """Per-industry plugin loaded from the `industry` query param."""

    industry: str | None = None

    action_creation_flow: list[ActionFlowEdge] = []

    action_creation_serializers = {
        Action.INIT: ConsumptionSerializer,
    }

    action_status_authorizations: dict[tuple[str, str], Callable[[Entity, Entity, Entity | None], bool]] = {}

    lookups = default_lookups
    excel_columns: list[dict] = [excel_column(key) for key in ACTION_EXCEL_COLUMNS]
    excel_import_serializer_class = ActionExcelImportSerializer
    write_actions = ("create", "destroy", "import_actions", "status")
    read_permission = HasEntityReadRights
    write_permission = HasEntityWriteRights
    admin_permission = None

    @classmethod
    def get_action_creation_serializers(cls):
        return {**ActionIndustryHandler.action_creation_serializers, **cls.action_creation_serializers}

    @classmethod
    def can_create_action(cls, action_type: str, status: str, parent: Action | None = None) -> bool:
        parent_state = (parent.type, parent.status) if parent is not None else None
        return (parent_state, (action_type, status)) in cls.action_creation_flow

    @classmethod
    def can_assign_status(cls, actor: Entity, action_type: str, status: str, holder: Entity, parent: Action | None) -> bool:
        authorize = cls.action_status_authorizations.get((action_type, status))
        parent_holder = parent.holder if parent is not None else None
        return authorize is not None and authorize(actor, holder, parent_holder)

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
