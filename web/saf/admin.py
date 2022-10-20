from django.contrib import admin
from .models import SafTicketSource, SafTicket


@admin.register(SafTicketSource)
class SafTicketSourceAdmin(admin.ModelAdmin):
    list_display = (
        "carbure_id",
        "created_at",
        "added_by",
        "period",
        "total_volume",
        "assigned_volume",
        "feedstock",
        "biofuel",
        "country_of_origin",
    )
    list_filter = (
        "added_by",
        "period",
        "feedstock",
        "biofuel",
    )


@admin.register(SafTicket)
class SafTicketAdmin(admin.ModelAdmin):
    list_display = (
        "carbure_id",
        "created_at",
        "supplier",
        "period",
        "volume",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "client",
    )
    list_filter = (
        "supplier",
        "period",
        "feedstock",
        "biofuel",
        "client",
    )
