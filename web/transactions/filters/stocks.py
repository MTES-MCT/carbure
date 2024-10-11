import django_filters
from django.db.models import Q, Value
from django.db.models.functions import Coalesce

from core.models import CarbureStock


class StockFilter(django_filters.FilterSet):
    periods = django_filters.CharFilter(method="filter_periods")
    feedstocks = django_filters.CharFilter(field_name="feedstock__code", lookup_expr="in")
    biofuels = django_filters.CharFilter(field_name="biofuel__code", lookup_expr="in")
    countries_of_origin = django_filters.CharFilter(field_name="country_of_origin__code_pays", lookup_expr="in")
    depots = django_filters.CharFilter(field_name="depot__name", lookup_expr="in")
    suppliers = django_filters.CharFilter(method="filter_suppliers")
    production_sites = django_filters.CharFilter(method="filter_production_sites")
    clients = django_filters.CharFilter(field_name="carbure_client__name", lookup_expr="in")
    query = django_filters.CharFilter(method="filter_query")
    selection = django_filters.ModelMultipleChoiceFilter(queryset=CarbureStock.objects.all(), field_name="pk")
    blacklist = django_filters.CharFilter(method="apply_blacklist")

    ordering = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("remaining_volume", "remaining_volume"),
            ("biofuel__name", "biofuel"),
            ("carbure_supplier__name", "supplier"),
            ("country_of_origin__name", "country"),
        ),
        field_labels={
            "id": "ID",
            "remaining_volume": "Remaining Volume",
            "biofuel__name": "Biofuel",
            "carbure_supplier__name": "Supplier",
            "country_of_origin__name": "Country of Origin",
        },
        method="filter_ordering",
    )

    class Meta:
        model = CarbureStock
        fields = []

    def filter_ordering(self, queryset, name, value):
        # Récupérer le champ à trier et l'ordre
        sort_by = value[0].lstrip("-")
        order = "desc" if value[0].startswith("-") else "asc"

        if sort_by == "biofuel":
            # Cas particulier pour le tri sur biofuel
            if order == "desc":
                return queryset.order_by("-biofuel__name", "-remaining_volume")
            else:
                return queryset.order_by("biofuel__name", "remaining_volume")

        if sort_by == "supplier":
            # Cas particulier pour le tri sur supplier (carbure_supplier ou unknown_supplier)
            queryset = queryset.annotate(vendor=Coalesce("carbure_supplier__name", "unknown_supplier", Value("")))
            if order == "desc":
                return queryset.order_by("-vendor")
            else:
                return queryset.order_by("vendor")

        # Si aucun cas particulier, utiliser le tri standard
        return queryset.order_by(value[0])

    def apply_blacklist(self, queryset, name, value):
        blacklist = value.split(",")
        self.blacklist = blacklist
        return queryset

    def is_field_blacklisted(self, field_name):
        return field_name in getattr(self, "blacklist", [])

    def filter_periods(self, queryset, name, value):
        if self.is_field_blacklisted("periods"):
            return queryset
        periods = value.split(",")
        return queryset.filter(
            Q(parent_lot__period__in=periods) | Q(parent_transformation__source_stock__parent_lot__period__in=periods)
        )

    def filter_suppliers(self, queryset, name, value):
        if self.is_field_blacklisted("suppliers"):
            return queryset
        suppliers = value.split(",")
        return queryset.filter(Q(carbure_supplier__name__in=suppliers) | Q(unknown_supplier__in=suppliers))

    def filter_production_sites(self, queryset, name, value):
        if self.is_field_blacklisted("production_sites"):
            return queryset
        production_sites = value.split(",")
        return queryset.filter(
            Q(carbure_production_site__name__in=production_sites) | Q(unknown_production_site__in=production_sites)
        )

    def filter_query(self, queryset, name, value):
        if self.is_field_blacklisted("query"):
            return queryset
        return queryset.filter(
            Q(feedstock__name__icontains=value)
            | Q(biofuel__name__icontains=value)
            | Q(carbure_id__icontains=value)
            | Q(country_of_origin__name__icontains=value)
            | Q(depot__name__icontains=value)
            | Q(parent_lot__free_field__icontains=value)
            | Q(parent_lot__transport_document_reference__icontains=value)
        )
