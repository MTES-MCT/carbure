import django_filters
from django.db import models
from django.db.models import Q
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField

from core.helpers import get_lots_with_deadline, get_lots_with_errors
from core.models import CarbureLot, Entity

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
    periods = django_filters.BaseInFilter(field_name="period", lookup_expr="in")
    production_sites = django_filters.BaseInFilter(method="filter_production_sites")
    delivery_sites = django_filters.BaseInFilter(method="filter_delivery_sites")
    feedstocks = django_filters.BaseInFilter(field_name="feedstock", lookup_expr="in")
    countries_of_origin = django_filters.BaseInFilter(field_name="country_of_origin__code_pays", lookup_expr="in")
    biofuels = django_filters.BaseInFilter(field_name="biofuel__code", lookup_expr="in")
    clients = django_filters.BaseInFilter(method="filter_clients")
    suppliers = django_filters.BaseInFilter(method="filter_suppliers")
    correction_status = django_filters.BaseInFilter(field_name="correction_status", lookup_expr="in")
    delivery_types = django_filters.BaseInFilter(field_name="delivery_type", lookup_expr="in")
    lot_status = django_filters.CharFilter(field_name="lot_status", lookup_expr="in")
    category = django_filters.CharFilter(method="filter_category")
    scores = django_filters.CharFilter(field_name="data_reliability_score", lookup_expr="in")
    added_by = django_filters.BaseInFilter(method="filter_added_by", label="Added by")
    conformity = django_filters.BaseInFilter(field_name="audit_status", lookup_expr="in")
    ml_scoring = django_filters.BaseInFilter(method="filter_ml_scoring", label="ML Scoring")

    selection = django_filters.BaseInFilter(method="filter_selection", label="Selection")
    errors = django_filters.BaseInFilter(method="filter_errors", label="Errors")
    client_types = django_filters.BaseInFilter(method="filter_client_types", label="Client types")
    invalid = django_filters.BooleanFilter(method="filter_invalid", label="Invalid")
    deadline = django_filters.BooleanFilter(method="filter_deadline", label="Deadline")
    history = django_filters.BooleanFilter(method="filter_history", label="History")
    correction = django_filters.BooleanFilter(method="filter_correction", label="Correction")
    order = django_filters.OrderingFilter(
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

    def filter_correction(self, queryset, name, value):
        return queryset

    def filter_history(self, queryset, name, value):
        return queryset

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

    @extend_schema_field(CharField(help_text="Comma-separated list of production sites"))
    def filter_production_sites(self, queryset, name, value):
        production_sites = value
        if production_sites:
            production_site_filter = Q(carbure_production_site__name__in=production_sites) | Q(
                unknown_production_site__in=production_sites
            )
            if "UNKNOWN" in production_sites:
                production_site_filter |= Q(carbure_production_site__isnull=True) & (
                    Q(unknown_production_site=None) | Q(unknown_production_site="")
                )
            return queryset.filter(production_site_filter)
        return queryset

    @extend_schema_field(CharField(help_text="Comma-separated list of delivery sites"))
    def filter_delivery_sites(self, queryset, name, value):
        delivery_sites = value
        if delivery_sites:
            delivery_site_filter = Q(carbure_delivery_site__name__in=delivery_sites) | Q(
                unknown_delivery_site__in=delivery_sites
            )
            if "UNKNOWN" in delivery_sites:
                delivery_site_filter |= Q(carbure_delivery_site__isnull=True) & (
                    Q(unknown_delivery_site=None) | Q(unknown_delivery_site="")
                )
            return queryset.filter(delivery_site_filter)
        return queryset

    @extend_schema_field(CharField(help_text="Comma-separated list of clients"))
    def filter_clients(self, queryset, name, value):
        clients = value
        if clients:
            client_filter = Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients)
            if "UNKNOWN" in clients:
                client_filter |= Q(carbure_client__isnull=True) & (Q(unknown_client=None) | Q(unknown_client=""))
            return queryset.filter(client_filter)
        return queryset

    @extend_schema_field(CharField(help_text="Comma-separated list of suppliers"))
    def filter_suppliers(self, queryset, name, value):
        suppliers = value
        if suppliers:
            supplier_filter = Q(carbure_supplier__name__in=suppliers) | Q(unknown_supplier__in=suppliers)
            if "UNKNOWN" in suppliers:
                supplier_filter |= Q(carbure_supplier__isnull=True) & (Q(unknown_supplier=None) | Q(unknown_supplier=""))
            return queryset.filter(supplier_filter)
        return queryset

    def filter_category(self, queryset, name, value):
        if value == "stocks":
            return queryset.filter(parent_stock__isnull=False)
        elif value == "imported":
            return queryset.filter(parent_stock__isnull=True)
        return queryset

    def filter_added_by(self, queryset, name, value):
        if value:
            return queryset.filter(added_by__name__in=value)
        return queryset

    def filter_ml_scoring(self, queryset, name, value):
        ml = value
        ml_filter = Q()
        if "OK" in ml:
            ml_filter |= Q(ml_control_requested=False)
        if "KO" in ml:
            ml_filter |= Q(ml_control_requested=True)
        return queryset.filter(ml_filter)

    @extend_schema_field(CharField(help_text="Comma-separated list of selections"))
    def filter_selection(self, queryset, name, value):
        if value:
            return queryset.filter(pk__in=value)
        return queryset

    @extend_schema_field(CharField(help_text="Comma-separated list of errors"))
    def filter_errors(self, queryset, name, value):
        if value:
            return queryset.filter(genericerror__error__in=value)
        return queryset

    @extend_schema_field(CharField(help_text="Comma-separated list of client types"))
    def filter_client_types(self, queryset, name, value):
        if value:
            client_type_filter = Q(carbure_client__entity_type__in=value)
            if Entity.UNKNOWN in value:
                client_type_filter = client_type_filter | Q(carbure_client__isnull=True)
            return queryset.filter(client_type_filter)
        return queryset

    def filter_invalid(self, queryset, name, value):
        if value:
            entity_id = self.request.query_params.get("entity_id")
            entity = Entity.objects.get(id=entity_id)
            will_aggregate = self.request.query_params.get("will_aggregate", "false").lower() == "true"
            return get_lots_with_errors(queryset, entity, will_aggregate=will_aggregate)
        return queryset

    def filter_deadline(self, queryset, name, value):
        if value:
            return get_lots_with_deadline(queryset)
        return queryset
