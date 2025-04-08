from django.db.models import Q
from django_filters import CharFilter, DateFilter, FilterSet, OrderingFilter
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField, ChoiceField, ListField

from tiruert.models import ElecOperation


class ElecOperationFilter(FilterSet):
    entity_id = CharFilter(method="filter_entity")
    date_from = DateFilter(field_name="created_at", lookup_expr="gte")
    date_to = DateFilter(field_name="created_at", lookup_expr="lte")
    operation = CharFilter(method="filter_operation")
    status = CharFilter(method="filter_status")
    from_to = CharFilter(method="filter_from_to")
    type = CharFilter(method="filter_type")
    period = CharFilter(method="filter_period")

    order_by = OrderingFilter(fields=(("created_at", "created_at"),))

    def filter_multiple_values(self, queryset, field_name, param_name):
        values = self.data.getlist(param_name)
        if values:
            return queryset.filter(Q(**{f"{field_name}__in": values}))
        return queryset

    @extend_schema_field(ListField(child=ChoiceField(choices=ElecOperation.OPERATION_STATUSES)))
    def filter_status(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "status", "status")

    def filter_entity(self, queryset, name, value):
        return queryset.filter(Q(credited_entity=value) | Q(debited_entity=value)).distinct()

    def filter_from_to(self, queryset, name, value):
        entities = self.request.GET.getlist(name)
        return queryset.filter(Q(credited_entity__name__in=entities) | Q(debited_entity__name__in=entities)).distinct()

    @extend_schema_field(ListField(child=ChoiceField(choices=["CREDIT", "DEBIT"])))
    def filter_type(self, queryset, name, value):
        value = value.upper()
        if value == "CREDIT":
            return queryset.filter(type__in=["ACQUISITION_FROM_CPO", "ACQUISITION"]).distinct()
        elif value == "DEBIT":
            return queryset.filter(type__in=["CESSION", "TENEUR"]).distinct()
        else:
            return queryset

    @extend_schema_field(ListField(child=CharField()))
    def filter_period(self, queryset, name, value):
        periods = self.request.GET.getlist(name)
        if not periods:
            return queryset

        q_objects = Q()
        for period in periods:
            q_objects |= Q(created_at__year=period[:4], created_at__month=period[4:])
        return queryset.filter(q_objects).distinct()

    @extend_schema_field(
        ListField(
            child=ChoiceField(
                choices=ElecOperation.OPERATION_TYPES + ("ACQUISITION", "ACQUISITION"),
            )
        )
    )
    def filter_operation(self, queryset, name, value):
        entity_id = self.request.query_params.get("entity_id")
        operations = [operation.upper() for operation in self.request.GET.getlist(name)]
        if not operations:
            return queryset
        q_objects = Q()
        if "ACQUISITION" in operations:
            q_objects |= Q(type="CESSION", credited_entity_id=entity_id)
            operations.remove("ACQUISITION")
        if "CESSION" in operations:
            q_objects |= Q(type="CESSION", debited_entity_id=entity_id)
            operations.remove("CESSION")
        q_objects |= Q(type__in=operations)
        return queryset.filter(q_objects).distinct()
