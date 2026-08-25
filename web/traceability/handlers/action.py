from typing import ClassVar

from core.permissions import HasEntityReadRights, HasEntityWriteRights


class ActionIndustryHandler:
    """Per-industry plugin loaded from the `industry` query param."""

    industry: str | None = None
    excel_column_labels: ClassVar[dict[str, str]] = {}

    @staticmethod
    def get_permissions(action: str):
        if action in ["create", "update", "partial_update", "destroy"]:
            return [HasEntityWriteRights()]
        return [HasEntityReadRights()]
