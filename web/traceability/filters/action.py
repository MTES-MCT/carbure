from django_filters import FilterSet, MultipleChoiceFilter, NumberFilter, OrderingFilter

from core.filters import MultiValueInFilter
from traceability.models import Action, ActionStatus


class ActionFilter(FilterSet):
    year = NumberFilter(field_name="working_date__year")
    type = MultipleChoiceFilter(field_name="type", choices=Action.TYPES)
    status = MultipleChoiceFilter(field_name="status", choices=ActionStatus.STATUSES)
    holder = MultiValueInFilter(field_name="holder__name")
    material = MultiValueInFilter(field_name="material__code")
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
            ("working_date", "working_date"),
        )
    )

    class Meta:
        model = Action
        fields = []
