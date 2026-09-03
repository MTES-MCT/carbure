from decimal import Decimal

import traceability.handlers.lookups as default_lookups
from core.permissions import HasEntityReadRights, HasEntityWriteRights
from traceability.handlers.excel import ACTION_EXCEL_COLUMNS, excel_column
from traceability.models import Action
from traceability.serializers.action import ActionExcelImportSerializer


class ActionIndustryHandler:
    """Per-industry plugin loaded from the `industry` query param."""

    industry: str | None = None
    lookups = default_lookups
    excel_columns: list[dict] = [excel_column(key) for key in ACTION_EXCEL_COLUMNS]
    excel_import_serializer_class = ActionExcelImportSerializer
    write_actions = ("destroy", "import_actions")
    units = ["MJ"]
    excel_quantity_unit = "MJ"

    @classmethod
    def get_permissions(cls, action: str):
        if action in cls.write_actions:
            return [HasEntityWriteRights()]
        return [HasEntityReadRights()]

    def to_mj(self, quantity: Decimal, _unit: str, _action: Action | None = None) -> Decimal:
        return quantity

    def from_mj(self, quantity_mj: Decimal, _unit: str, _action: Action | None = None) -> Decimal:
        return quantity_mj
