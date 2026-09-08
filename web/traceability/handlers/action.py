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

    @classmethod
    def get_permissions(cls, action: str):
        if action in cls.write_actions:
            return [HasEntityWriteRights()]
        return [HasEntityReadRights()]
