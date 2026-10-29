from django_filters.constants import EMPTY_VALUES

from core.filters import MultiValueInFilter
from traceability.models.material import Material
from traceability.services.column_groups import COLUMN_GROUPS
from traceability.services.parent_chain import chain_column, filter_by_chain


class RecursiveColumnFilter(MultiValueInFilter):
    """One column of a group declared in ``services/column_groups.py``.

    Does not query by itself. When its query param is set, it calls ``RecursiveFilter``,
    which applies every active column in one walk.
    Subclass, set ``group`` and ``column``, and declare the subclass on ``ActionFilter``.
    Walkthrough: ``traceability/docs/parent_chain.md``.
    """

    column: str
    group: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "group" not in cls.__dict__ and "column" not in cls.__dict__:
            return
        group = cls.__dict__.get("group")
        column = cls.__dict__.get("column")
        if not isinstance(group, str) or not isinstance(column, str):
            raise ValueError(f"{cls.__name__} must set group and column")
        if group not in COLUMN_GROUPS:
            raise ValueError(f"{cls.__name__}.group {group!r} is not in COLUMN_GROUPS")
        if column not in COLUMN_GROUPS[group].start():
            raise ValueError(f"{cls.__name__}.column {column!r} is not produced by group {group!r}")

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        return RecursiveFilter(self.parent).filter(qs)

    def selected_values(self):
        """None when the query param is absent. Empty when no stored id matches."""
        raw = self._raw_values()
        if not raw:
            return None
        return self.to_values(raw)

    def distinct_values(self, queryset):
        stored = [
            stored_value
            for _action_id, stored_value in chain_column(queryset, self.column, [self.group])
            if stored_value is not None
        ]
        return self.to_labels(stored)

    def to_values(self, raw):
        return raw

    def to_labels(self, stored):
        return sorted(set(stored))

    def _raw_values(self):
        data = getattr(self.parent, "data", None)
        if not hasattr(data, "getlist"):
            return []
        key = self._get_query_param_name()
        return [item for item in data.getlist(key) if item not in (None, "")]


class RecursiveFilter:
    """One walk for every recursive column present on the request.

    A column filter calls it only when that column's query param is set.
    The first call applies every selected column. Later calls return the queryset unchanged.
    """

    def __init__(self, filterset):
        self.filterset = filterset

    def filter(self, queryset):
        if getattr(self.filterset, "_recursive_applied", False):
            return queryset
        self.filterset._recursive_applied = True

        columns = {}
        groups = []
        for filter_obj in self.filterset.filters.values():
            if not isinstance(filter_obj, RecursiveColumnFilter):
                continue
            values = filter_obj.selected_values()
            if values is None:
                continue
            if not values:
                return queryset.none()
            columns[filter_obj.column] = values
            groups.append(filter_obj.group)
        return filter_by_chain(queryset, columns, groups)


class OriginMaterialFilter(RecursiveColumnFilter):
    """First declared material from the root. The query param is a material code."""

    column = "origin_material_id"
    group = "inherited_fields"

    def to_values(self, codes):
        return list(Material.objects.filter(code__in=codes).values_list("pk", flat=True))

    def to_labels(self, material_ids):
        codes = Material.objects.filter(pk__in=material_ids).order_by("code")
        return codes.values_list("code", flat=True)
