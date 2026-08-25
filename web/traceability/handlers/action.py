from typing import ClassVar

from core.permissions import HasEntityReadRights, HasEntityWriteRights


class ActionIndustryLookups:
    """Per-industry select values, keyed by Action field name."""


class ActionIndustryHandler:
    """Per-industry plugin loaded from the `industry` query param."""

    industry: str | None = None
    excel_column_labels: ClassVar[dict[str, str]] = {}
    lookups_class: ClassVar[type[ActionIndustryLookups]] = ActionIndustryLookups

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
        if action in ["create", "update", "partial_update", "destroy"]:
            return [HasEntityWriteRights()]
        return [HasEntityReadRights()]
