from django.contrib import admin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from core.import_export_template import ImportExportWithTemplateModelAdmin
from saf.models.constants import SAF_DEPOT_TYPES
from saf.models.saf_logistics import SafLogistics
from transactions.models.airport import Airport
from transactions.models.depot import Depot

from .models import SafTicket, SafTicketSource


@admin.register(SafTicketSource)
class SafTicketSourceAdmin(admin.ModelAdmin):
    list_display = (
        "carbure_id",
        "created_at",
        "added_by",
        "delivery_period",
        "total_volume",
        "assigned_volume",
        "feedstock",
        "biofuel",
        "country_of_origin",
    )
    list_filter = (
        "added_by",
        "delivery_period",
        "feedstock",
        "biofuel",
    )
    search_fields = [
        "carbure_id",
        "added_by__name",
    ]
    raw_id_fields = [
        "parent_lot",
        "parent_ticket",
        "origin_lot",
    ]
    autocomplete_fields = [
        "carbure_producer",
        "carbure_production_site",
        "added_by",
        "origin_lot_site",
    ]

    # Optimize queries for list view
    list_select_related = [
        "added_by",
        "feedstock",
        "biofuel",
        "country_of_origin",
    ]


@admin.register(SafTicket)
class SafTicketAdmin(admin.ModelAdmin):
    list_display = (
        "carbure_id",
        "created_at",
        "supplier",
        "assignment_period",
        "volume",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "client",
    )
    list_filter = (
        "supplier",
        "assignment_period",
        "feedstock",
        "biofuel",
        "client",
    )
    search_fields = [
        "carbure_id",
        "supplier__name",
        "client__name",
    ]
    raw_id_fields = [
        "origin_lot",
    ]
    autocomplete_fields = [
        "biofuel",
        "feedstock",
        "country_of_origin",
        "supplier",
        "client",
        "carbure_producer",
        "carbure_production_site",
        "production_country",
        "parent_ticket_source",
        "reception_airport",
        "origin_lot_site",
    ]

    # Optimize queries for list view
    list_select_related = [
        "supplier",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "client",
    ]

    # Optimize queries for detail/change view
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "supplier",
            "client",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "carbure_producer",
            "carbure_production_site",
            "carbure_production_site__created_by",
            "production_country",
            "reception_airport",
            "reception_airport__created_by",
            # parent_ticket_source and its nested relations
            "parent_ticket_source",
            "parent_ticket_source__added_by",
            "parent_ticket_source__feedstock",
            "parent_ticket_source__biofuel",
            "parent_ticket_source__country_of_origin",
            "parent_ticket_source__carbure_producer",
            "parent_ticket_source__carbure_production_site",
            "parent_ticket_source__carbure_production_site__created_by",
            "parent_ticket_source__production_country",
            "parent_ticket_source__origin_lot_site",
            "parent_ticket_source__origin_lot_site__created_by",
            # origin_lot and its nested relations
            "origin_lot",
            "origin_lot__carbure_client",
            "origin_lot__carbure_producer",
            "origin_lot__carbure_supplier",
            "origin_lot__carbure_production_site",
            "origin_lot__carbure_production_site__created_by",
            "origin_lot__carbure_dispatch_site",
            "origin_lot__carbure_dispatch_site__created_by",
            "origin_lot__carbure_delivery_site",
            "origin_lot__carbure_delivery_site__created_by",
            "origin_lot__feedstock",
            "origin_lot__biofuel",
            "origin_lot__country_of_origin",
            "origin_lot_site",
            "origin_lot_site__created_by",
        )


class SafLogisticsResource(resources.ModelResource):
    origin_depot = fields.Field(
        attribute="origin_depot",
        widget=ForeignKeyWidget(Depot, field="name"),
    )
    destination_airport = fields.Field(
        attribute="destination_airport",
        widget=ForeignKeyWidget(Airport, field="name"),
    )

    class Meta:
        model = SafLogistics
        import_id_fields = ["origin_depot", "destination_airport", "shipping_method"]
        skip_unchanged = True
        report_skipped = True


@admin.register(SafLogistics)
class SafLogisticsAdmin(ImportExportWithTemplateModelAdmin):
    resource_classes = [SafLogisticsResource]

    list_display = [
        "id",
        "origin_depot__name",
        "destination_airport__name",
        "has_intermediary_depot",
        "shipping_method",
    ]

    list_filter = [
        "origin_depot__name",
        "destination_airport__name",
        "has_intermediary_depot",
        "shipping_method",
    ]

    search_fields = [
        "origin_depot__name",
        "destination_airport__name",
    ]

    import_template_columns = [
        {
            "header": "origin_depot",
            "options": (Depot.objects.filter(site_type__in=SAF_DEPOT_TYPES).order_by("name").values_list("name", flat=True)),
        },
        {
            "header": "destination_airport",
            "options": Airport.objects.order_by("name").values_list("name", flat=True),
        },
        {
            "header": "shipping_method",
            "options": [method for method, _ in SafLogistics.SHIPPING_METHODS],
        },
        {
            "header": "has_intermediary_depot",
            "options": ["TRUE", "FALSE"],
        },
    ]
