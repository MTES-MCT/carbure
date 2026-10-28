from django_filters import FilterSet, MultipleChoiceFilter, NumberFilter, OrderingFilter

from core.filters import MultiValueInFilter
from traceability.models import Action, ActionStatus
from traceability.models.material import Material
from traceability.services.parent_chain import filter_by_origin_material, origin_material_ids


class OriginMaterialFilter(MultiValueInFilter):
    """Filter on the first material declared from the root.

    The walk runs on the queryset already narrowed by the other filters.
    """

    def filter(self, qs, value):
        codes = self._codes(value)
        if not codes:
            return qs
        material_ids = list(Material.objects.filter(code__in=codes).values_list("pk", flat=True))
        return filter_by_origin_material(qs, material_ids)

    def distinct_values(self, queryset):
        codes = Material.objects.filter(pk__in=origin_material_ids(queryset)).order_by("code")
        return codes.values_list("code", flat=True)

    def _codes(self, value):
        data = getattr(self.parent, "data", None)
        key = self._get_query_param_name()
        if hasattr(data, "getlist"):
            return [item for item in data.getlist(key) if item not in (None, "")]
        if isinstance(value, (list, tuple)):
            return [item for item in value if item not in (None, "")]
        if value in (None, ""):
            return []
        return [value]


class ActionFilter(FilterSet):
    year = NumberFilter(field_name="working_date__year")
    period = MultiValueInFilter(field_name="period")
    type = MultipleChoiceFilter(field_name="type", choices=Action.TYPES)
    status = MultipleChoiceFilter(field_name="status", choices=ActionStatus.STATUSES)
    holder = MultiValueInFilter(field_name="holder__name")
    material = MultiValueInFilter(field_name="material__code")
    origin_material = OriginMaterialFilter()
    site = MultiValueInFilter(field_name="site__name")
    shipping_method = MultipleChoiceFilter(field_name="shipping_method", choices=Action.SHIPPING_METHODS)

    order_by = OrderingFilter(
        fields=(
            ("pos_id", "pos_id"),
            ("holder__name", "holder"),
            ("material__name", "material"),
            ("quantity", "quantity"),
            ("site__name", "site"),
            ("shipping_distance", "shipping_distance"),
            ("status", "status"),
            ("working_date", "working_date"),
        )
    )

    class Meta:
        model = Action
        fields = []
