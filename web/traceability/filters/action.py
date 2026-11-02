from django_filters import FilterSet, MultipleChoiceFilter, NumberFilter, OrderingFilter

from core.filters import MultiValueInFilter
from traceability.filters.recursive import OriginMaterialFilter
from traceability.models import Action, ActionStatus


class ActionOrderingFilter(OrderingFilter):
    def filter(self, qs, value):
        # status is absent when the list is too large for the correlated subquery.
        if value and "status" not in qs.query.annotations:
            value = [item for item in value if item.lstrip("-") != "status"]
        if not value:
            return qs
        return super().filter(qs, value)


class ActionFilter(FilterSet):
    # MultipleChoiceFilter met distinct=True par défaut, pour les relations qui dupliquent
    # les lignes. Ces champs sont des colonnes de l'action : le DISTINCT transformait le
    # COUNT de pagination en dédoublonnage de toutes les colonnes, sans changer le total.
    year = NumberFilter(field_name="working_date__year")
    period = MultiValueInFilter(field_name="period")
    type = MultipleChoiceFilter(field_name="type", choices=Action.TYPES, distinct=False)
    status = MultipleChoiceFilter(
        field_name="status", choices=ActionStatus.STATUSES, distinct=False, method="filter_status"
    )
    holder = MultiValueInFilter(field_name="holder__name")
    material = MultiValueInFilter(field_name="material__code")
    site = MultiValueInFilter(field_name="site__name")
    shipping_method = MultipleChoiceFilter(field_name="shipping_method", choices=Action.SHIPPING_METHODS, distinct=False)
    origin_material = OriginMaterialFilter()

    order_by = ActionOrderingFilter(
        fields=(
            ("pos_id", "pos_id"),
            ("holder__name", "holder"),
            ("material__name", "material"),
            ("quantity", "quantity"),
            ("site__name", "site"),
            ("shipping_distance", "shipping_distance"),
            ("status", "status"),
            ("type", "type"),
            ("working_date", "working_date"),
        )
    )

    class Meta:
        model = Action
        fields = []

    def filter_status(self, queryset, name, value):
        if "status" not in queryset.query.annotations:
            return queryset
        return queryset.filter(**{f"{name}__in": value})
