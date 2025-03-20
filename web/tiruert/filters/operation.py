from django.db.models import Q
from django_filters import CharFilter, DateFilter, FilterSet
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField, ChoiceField, ListField

from core.models import MatierePremiere
from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.models.operation import Operation


class OperationFilter(FilterSet):
    entity_id = CharFilter(method="filter_entity")
    date_from = DateFilter(field_name="created_at", lookup_expr="gte")
    date_to = DateFilter(field_name="created_at", lookup_expr="lte")
    operation = CharFilter(method="filter_operation")
    status = CharFilter(method="filter_status")
    customs_category = CharFilter(method="filter_customs_category")
    biofuel = CharFilter(method="filter_biofuel")
    sector = CharFilter(method="filter_sector")
    from_to = CharFilter(method="filter_from_to")
    depot = CharFilter(method="filter_depot")
    type = CharFilter(method="filter_type")
    period = CharFilter(method="filter_period")

    def filter_multiple_values(self, queryset, field_name, param_name):
        values = self.data.getlist(param_name)
        if values:
            return queryset.filter(Q(**{f"{field_name}__in": values}))
        return queryset

    @extend_schema_field(ListField(child=CharField()))
    def filter_biofuel(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "biofuel__code", "biofuel")

    @extend_schema_field(ListField(child=ChoiceField(choices=MatierePremiere.MP_CATEGORIES)))
    def filter_customs_category(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "customs_category", "customs_category")

    @extend_schema_field(ListField(child=ChoiceField(choices=Operation.OPERATION_STATUSES)))
    def filter_status(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "status", "status")

    def filter_entity(self, queryset, name, value):
        return queryset.filter(Q(credited_entity=value) | Q(debited_entity=value)).distinct()

    @extend_schema_field(ListField(child=ChoiceField(choices=["ESSENCE", "GAZOLE", "CARBURÉACTEUR"])))
    def filter_sector(self, queryset, name, value):
        sectors = [sector.upper() for sector in self.request.GET.getlist(name)]
        if not sectors:
            return queryset

        q_objects = Q()
        if "ESSENCE" in sectors:
            q_objects |= Q(biofuel__compatible_essence=True)
        if "GAZOLE" in sectors:
            q_objects |= Q(biofuel__compatible_diesel=True)
        if "CARBURÉACTEUR" in sectors:
            q_objects |= Q(biofuel__code__in=SAF_BIOFUEL_TYPES)
        return queryset.filter(q_objects).distinct()

    def filter_from_to(self, queryset, name, value):
        entities = self.request.GET.getlist(name)
        return queryset.filter(Q(credited_entity__name__in=entities) | Q(debited_entity__name__in=entities)).distinct()

    @extend_schema_field(ListField(child=CharField()))
    def filter_depot(self, queryset, name, value):
        depots = self.request.GET.getlist(name)
        return queryset.filter(Q(from_depot__name__in=depots) | Q(to_depot__name__in=depots)).distinct()

    @extend_schema_field(ListField(child=ChoiceField(choices=["CREDIT", "DEBIT"])))
    def filter_type(self, queryset, name, value):
        value = value.upper()
        if value == "CREDIT":
            return queryset.filter(type__in=["INCORPORATION", "MAC_BIO", "LIVRAISON_DIRECTE", "ACQUISITION"]).distinct()
        elif value == "DEBIT":
            return queryset.filter(type__in=["CESSION", "TENEUR", "EXPORTATION", "DEVALUATION"]).distinct()
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
                choices=Operation.OPERATION_TYPES + ("ACQUISITION", "ACQUISITION"),
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
