from typing import ClassVar

from core.permissions import HasEntityReadRights, HasEntityWriteRights
from traceability.handlers.excel import ACTION_EXCEL_COLUMNS, excel_column


class ActionIndustryLookups:
    """Per-industry select values, keyed by Action field name."""


class ActionIndustryHandler:
    """Per-industry plugin loaded from the `industry` query param."""

    industry: str | None = None
    lookups_class: ClassVar[type[ActionIndustryLookups]] = ActionIndustryLookups
    excel_columns: ClassVar[list[dict]] = [excel_column(key) for key in ACTION_EXCEL_COLUMNS]
    write_actions = ("create", "update", "partial_update", "destroy", "import_actions")

    def __init__(self):
        self.lookups = self.lookups_class()

    def lookup(self, field: str, entity=None):
        """Return the queryset allowed for an Action field, or None."""
        method = getattr(self.lookups, field, None)
        if not callable(method):
            return None
        return method(entity)

    @staticmethod
    def get_permissions(action: str):
        if action in ActionIndustryHandler.write_actions:
            return [HasEntityWriteRights()]
        return [HasEntityReadRights()]
