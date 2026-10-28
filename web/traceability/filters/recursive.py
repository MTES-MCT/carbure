from django_filters.constants import EMPTY_VALUES

from core.filters import MultiValueInFilter
from core.models import Entity
from traceability.models.material import Material
from traceability.services.climbers import CLIMBERS
from traceability.services.parent_chain import chain_column, filter_by_chain
from transactions.models.site import Site


class RecursiveColumnFilter(MultiValueInFilter):
    """One column of a climber declared in ``services/climbers.py``.

    Does not query by itself. When its query param is set, it calls ``RecursiveFilter``,
    which applies every active column in one walk.
    Subclass, set ``climber`` and ``column``, and declare the subclass on ``ActionFilter``.
    """

    column: str
    climber: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "climber" not in cls.__dict__ and "column" not in cls.__dict__:
            return
        climber = cls.__dict__.get("climber")
        column = cls.__dict__.get("column")
        if not isinstance(climber, str) or not isinstance(column, str):
            raise ValueError(f"{cls.__name__} must set climber and column")
        if climber not in CLIMBERS:
            raise ValueError(f"{cls.__name__}.climber {climber!r} is not in CLIMBERS")
        if column not in CLIMBERS[climber].start():
            raise ValueError(f"{cls.__name__}.column {column!r} is not produced by climber {climber!r}")

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
            for _action_id, stored_value in chain_column(queryset, self.column, [self.climber])
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
        climbers = []
        for filter_obj in self.filterset.filters.values():
            if not isinstance(filter_obj, RecursiveColumnFilter):
                continue
            values = filter_obj.selected_values()
            if values is None:
                continue
            if not values:
                return queryset.none()
            columns[filter_obj.column] = values
            climbers.append(filter_obj.climber)
        return filter_by_chain(queryset, columns, climbers)


class OriginMaterialFilter(RecursiveColumnFilter):
    """First declared material from the root. The query param is a material code."""

    column = "origin_material_id"
    climber = "inherited_fields"

    def to_values(self, codes):
        return list(Material.objects.filter(code__in=codes).values_list("pk", flat=True))

    def to_labels(self, material_ids):
        codes = Material.objects.filter(pk__in=material_ids).order_by("code")
        return codes.values_list("code", flat=True)


class ProducerFilter(RecursiveColumnFilter):
    """Holder of the root action. The query param is the entity name."""

    column = "root_holder_id"
    climber = "inherited_fields"

    def to_values(self, names):
        return list(Entity.objects.filter(name__in=names).values_list("pk", flat=True))

    def to_labels(self, holder_ids):
        names = Entity.objects.filter(pk__in=holder_ids).order_by("name")
        return names.values_list("name", flat=True)


class RootPosFilter(RecursiveColumnFilter):
    """pos_id of the root action. The query param is that pos_id."""

    column = "root_pos_id"
    climber = "inherited_fields"


class NearestSiteFilter(RecursiveColumnFilter):
    """First site set above the action. The action's own site is ignored."""

    column = "nearest_site_id"
    climber = "inherited_fields"

    def to_values(self, names):
        return list(Site.objects.filter(name__in=names).values_list("pk", flat=True))

    def to_labels(self, site_ids):
        names = Site.objects.filter(pk__in=site_ids).order_by("name")
        return names.values_list("name", flat=True)
