import django_filters
from django.db import models
from django.db.models import Q

from core.helpers import get_lots_with_deadline, get_lots_with_errors
from core.models import CarbureLot

from .utils import is_admin_user, is_auditor_user


class CarbureLotStatus(models.TextChoices):
    DRAFTS = "DRAFTS", "DRAFTS"
    IN = "IN", "IN"
    OUT = "OUT", "OUT"
    DECLARATION = "DECLARATION", "DECLARATION"
    ALERTS = "ALERTS", "ALERTS"
    LOTS = "LOTS", "LOTS"


class LotsFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=CarbureLotStatus.choices, method="filter_status")
    year = django_filters.NumberFilter(field_name="year")
    periods = django_filters.CharFilter(method="filter_periods")
    production_sites = django_filters.CharFilter(method="filter_production_sites")
    delivery_sites = django_filters.CharFilter(method="filter_delivery_sites")
    feedstocks = django_filters.CharFilter(method="filter_feedstocks")
    countries_of_origin = django_filters.CharFilter(method="filter_countries_of_origin")
    biofuels = django_filters.CharFilter(method="filter_biofuels")
    clients = django_filters.CharFilter(method="filter_clients")
    suppliers = django_filters.CharFilter(method="filter_suppliers")
    correction_status = django_filters.CharFilter(method="filter_correction_status")
    delivery_types = django_filters.CharFilter(method="filter_delivery_types")
    lot_status = django_filters.CharFilter(field_name="lot_status", lookup_expr="in")
    category = django_filters.CharFilter(method="filter_category")
    scores = django_filters.CharFilter(field_name="data_reliability_score", lookup_expr="in")
    added_by = django_filters.CharFilter(method="filter_added_by")
    conformity = django_filters.CharFilter(field_name="audit_status", lookup_expr="in")
    ml_scoring = django_filters.CharFilter(method="filter_ml_scoring")

    selection = django_filters.CharFilter(method="filter_selection")
    errors = django_filters.CharFilter(method="filter_errors")
    invalid = django_filters.BooleanFilter(method="filter_invalid")
    deadline = django_filters.BooleanFilter(method="filter_deadline")

    ordering = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("volume", "volume"),
            ("biofuel__name", "biofuel"),
            ("carbure_client__name", "client"),
            ("carbure_supplier__name", "supplier"),
            ("delivery_date", "period"),
            ("feedstock__name", "feedstock"),
            ("ghg_reduction", "ghg_reduction"),
            ("volume", "volume"),
            ("country_of_origin__name", "country_of_origin"),
            ("added_by__name", "added_by"),
        ),
        field_labels={
            "biofuel__name": "Biofuel Name",
            "client": "Client",
            "supplier": "Supplier",
            "delivery_date": "Period",
            "feedstock__name": "Feedstock",
            "ghg_reduction": "GHG Reduction",
            "volume": "Volume",
            "country_of_origin__name": "Country of Origin",
            "added_by__name": "Added By",
        },
    )

    class Meta:
        model = CarbureLot
        fields = []

    def filter_status(self, queryset, name, value):
        entity = self.data.get("entity_id")

        if is_admin_user(self.request, entity):
            queryset = queryset.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])

            if value == "ALERTS":
                queryset = queryset.exclude(audit_status=CarbureLot.CONFORM).filter(
                    Q(highlighted_by_admin=True) | Q(random_control_requested=True) | Q(ml_control_requested=True)
                )
            elif value == "LOTS":
                queryset = queryset.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])

            return queryset

        if is_auditor_user(entity):
            if value == "ALERTS":
                queryset = queryset.exclude(audit_status=CarbureLot.CONFORM).filter(
                    Q(highlighted_by_auditor=True) | Q(random_control_requested=True) | Q(ml_control_requested=True)
                )
            elif value == "LOTS":
                queryset = queryset.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
            return queryset

        if value == "DRAFTS":
            return queryset.filter(added_by_id=entity, lot_status=CarbureLot.DRAFT)
        elif value == "IN":
            return queryset.filter(carbure_client_id=entity).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        elif value == "OUT":
            return queryset.filter(carbure_supplier_id=entity).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        elif value == "DECLARATION":
            return queryset.filter(Q(carbure_supplier_id=entity) | Q(carbure_client_id=entity)).exclude(
                lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED]
            )

        return queryset.filter(Q(added_by_id=entity) | Q(carbure_supplier_id=entity) | Q(carbure_client_id=entity))

    def filter_periods(self, queryset, name, value):
        periods = value.split(",")
        return queryset.filter(period__in=periods)

    def filter_production_sites(self, queryset, name, value):
        production_sites = value.split(",")
        production_site_filter = Q(carbure_production_site__name__in=production_sites) | Q(
            unknown_production_site__in=production_sites
        )
        if "UNKNOWN" in production_sites:
            production_site_filter |= Q(carbure_production_site__isnull=True) & (
                Q(unknown_production_site=None) | Q(unknown_production_site="")
            )
        return queryset.filter(production_site_filter)

    def filter_delivery_sites(self, queryset, name, value):
        delivery_sites = value.split(",")
        delivery_site_filter = Q(carbure_delivery_site__name__in=delivery_sites) | Q(
            unknown_delivery_site__in=delivery_sites
        )
        if "UNKNOWN" in delivery_sites:
            delivery_site_filter |= Q(carbure_delivery_site__isnull=True) & (
                Q(unknown_delivery_site=None) | Q(unknown_delivery_site="")
            )
        return queryset.filter(delivery_site_filter)

    def filter_feedstocks(self, queryset, name, value):
        feedstocks = value.split(",")
        return queryset.filter(feedstock__code__in=feedstocks)

    def filter_countries_of_origin(self, queryset, name, value):
        countries_of_origin = value.split(",")
        return queryset.filter(country_of_origin__code_pays__in=countries_of_origin)

    def filter_biofuels(self, queryset, name, value):
        biofuels = value.split(",")
        return queryset.filter(biofuel__code__in=biofuels)

    def filter_clients(self, queryset, name, value):
        clients = value.split(",")
        client_filter = Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients)
        if "UNKNOWN" in clients:
            client_filter |= Q(carbure_client__isnull=True) & (Q(unknown_client=None) | Q(unknown_client=""))
        return queryset.filter(client_filter)

    def filter_suppliers(self, queryset, name, value):
        suppliers = value.split(",")
        supplier_filter = Q(carbure_supplier__name__in=suppliers) | Q(unknown_supplier__in=suppliers)
        if "UNKNOWN" in suppliers:
            supplier_filter |= Q(carbure_supplier__isnull=True) & (Q(unknown_supplier=None) | Q(unknown_supplier=""))
        return queryset.filter(supplier_filter)

    def filter_correction_status(self, queryset, name, value):
        correction_status = value.split(",")
        return queryset.filter(correction_status__in=correction_status)

    def filter_delivery_types(self, queryset, name, value):
        delivery_types = value.split(",")
        return queryset.filter(delivery_type__in=delivery_types)

    def filter_category(self, queryset, name, value):
        if value == "stocks":
            return queryset.filter(parent_stock__isnull=False)
        elif value == "imported":
            return queryset.filter(parent_stock__isnull=True)
        return queryset

    def filter_added_by(self, queryset, name, value):
        added_by = value.split(",")
        return queryset.filter(added_by__name__in=added_by)

    def filter_ml_scoring(self, queryset, name, value):
        ml = value.split(",")
        ml_filter = Q()
        if "OK" in ml:
            ml_filter |= Q(ml_control_requested=False)
        if "KO" in ml:
            ml_filter |= Q(ml_control_requested=True)
        return queryset.filter(ml_filter)

    def filter_selection(self, queryset, name, value):
        selection = value.split(",")
        if selection:
            return queryset.filter(pk__in=selection)
        return queryset

    def filter_errors(self, queryset, name, value):
        errors = value.split(",")
        return queryset.filter(genericerror__error__in=errors)

    def filter_invalid(self, queryset, name, value):
        if value:
            will_aggregate = self.request.query_params.get("will_aggregate", "false").lower() == "true"
            return get_lots_with_errors(queryset, self.request.entity, will_aggregate=will_aggregate)
        return queryset

    def filter_deadline(self, queryset, name, value):
        if value:
            return get_lots_with_deadline(queryset)
        return queryset
