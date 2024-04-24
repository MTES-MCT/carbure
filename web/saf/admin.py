from django.contrib import admin
from .models import SafTicketSource, SafTicket


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
