import traceability.handlers.lookups as default_lookups
from core.permissions import HasEntityReadRights, HasEntityWriteRights
from traceability.handlers.excel import ACTION_EXCEL_COLUMNS, excel_column


class ActionIndustryHandler:
    """Per-industry plugin loaded from the `industry` query param."""

    industry: str | None = None
    lookups = default_lookups
    excel_columns: list[dict] = [excel_column(key) for key in ACTION_EXCEL_COLUMNS]
    write_actions = ("create", "update", "partial_update", "destroy", "import_actions")

    @staticmethod
    def get_permissions(action: str):
        if action in ActionIndustryHandler.write_actions:
            return [HasEntityWriteRights()]
        return [HasEntityReadRights()]
