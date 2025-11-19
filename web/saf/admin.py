from django.contrib import admin

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
    autocomplete_fields = [
        "parent_lot",
        "parent_ticket",
        "carbure_producer",
        "carbure_production_site",
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
        "origin_lot",
        "origin_lot_site",
    ]
