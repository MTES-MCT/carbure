from django_filters import FilterSet, MultipleChoiceFilter, NumberFilter, OrderingFilter

from core.filters import MultiValueInFilter
from traceability.filters.recursive import NearestSiteFilter, OriginMaterialFilter, ProducerFilter, RootPosFilter
from traceability.models import Action, ActionStatus


class ActionFilter(FilterSet):
    # MultipleChoiceFilter met distinct=True par défaut, pour les relations qui dupliquent
    # les lignes. Ces champs sont des colonnes de l'action : le DISTINCT transformait le
    # COUNT de pagination en dédoublonnage de toutes les colonnes, sans changer le total.
    year = NumberFilter(field_name="working_date__year")
    period = MultiValueInFilter(field_name="period")
    type = MultipleChoiceFilter(field_name="type", choices=Action.TYPES, distinct=False)
    status = MultipleChoiceFilter(field_name="status", choices=ActionStatus.STATUSES, distinct=False)
    holder = MultiValueInFilter(field_name="holder__name")
    material = MultiValueInFilter(field_name="material__code")
    site = MultiValueInFilter(field_name="site__name")
    shipping_method = MultipleChoiceFilter(
        field_name="shipping_method", choices=Action.SHIPPING_METHODS, distinct=False
    )
    origin_material = OriginMaterialFilter()
    producer = ProducerFilter()
    root_pos = RootPosFilter()
    nearest_site = NearestSiteFilter()

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
