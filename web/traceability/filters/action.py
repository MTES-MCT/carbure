from django_filters import FilterSet, MultipleChoiceFilter, OrderingFilter

from core.filters import MultiValueInFilter
from traceability.models.action import Action


class ActionFilter(FilterSet):
    industry = MultipleChoiceFilter(field_name="industry", choices=Action.INDUSTRIES)
    type = MultipleChoiceFilter(field_name="type", choices=Action.TYPES)
    holder = MultiValueInFilter(field_name="holder__name")
    material = MultiValueInFilter(field_name="material__code")
    site = MultiValueInFilter(field_name="site__name")
    shipping_method = MultipleChoiceFilter(field_name="shipping_method", choices=Action.SHIPPING_METHODS)

    order_by = OrderingFilter(
        fields=(
            ("pos_id", "pos_id"),
            ("holder__name", "holder__name"),
            ("material__name", "material__name"),
            ("quantity", "quantity"),
            ("site__name", "site__name"),
            ("shipping_distance", "shipping_distance"),
        )
    )

    class Meta:
        model = Action
        fields = [
            "industry",
            "type",
            "holder",
            "material",
            "site",
            # "shipping_method",
        ]
